"""Design Workshop screen for creating and managing unit designs."""

import pygame
from game.data import constants
from game.data.constants import (COLOR_TEXT, COLOR_BUTTON, COLOR_BUTTON_HOVER,
                                 COLOR_BUTTON_BORDER, COLOR_BUTTON_HIGHLIGHT)
from game import unit_components


class DesignWorkshopScreen:
    """Manages the Design Workshop screen for unit design."""

    def __init__(self, font, small_font):
        """Initialize design workshop screen with fonts.

        Args:
            font: Main pygame font object
            small_font: Small pygame font object
        """
        self.font = font
        self.small_font = small_font

        # State
        self.design_workshop_open = False

        # UI state (designs are stored in faction.designs, not here)
        self.selected_slot = 0  # Currently selected slot (0-63)
        self.design_scroll_offset = 0
        self.designs_per_page = 8  # Show 8 slots at a time

        # Current design being edited (reflects selected slot)
        self.dw_selected_chassis = 'infantry'
        self.dw_selected_weapon = 'hand_weapons'
        self.dw_selected_armor = 'no_armor'
        self.dw_selected_reactor = 'fission'
        self.dw_selected_ability1 = 'none'
        self.dw_selected_ability2 = 'none'

        # Which component panel is currently being edited
        self.dw_editing_panel = None
        self.dw_ability_scroll_offset = 0

        # UI elements
        self.dw_left_arrow_rect = None
        self.dw_right_arrow_rect = None
        self.dw_design_rects = []
        self.dw_apply_rect = None
        self.dw_done_rect = None
        self.dw_rename_rect = None
        self.dw_obsolete_rect = None
        self.dw_disband_rect = None
        self.dw_cancel_rect = None
        self.dw_chassis_rect = None
        self.dw_weapon_rect = None
        self.dw_armor_rect = None
        self.dw_reactor_rect = None
        self.dw_ability1_rect = None
        self.dw_ability2_rect = None
        self.dw_component_selection_rects = []
        self.dw_component_cancel_rect = None
        self.dw_ability_up_arrow = None
        self.dw_ability_down_arrow = None

        # Rename popup state
        self.rename_popup_open = False
        self.rename_text_input = ""
        self.rename_text_selected = False  # Track if text is selected
        self.dw_rename_ok_rect = None
        self.dw_rename_cancel_rect = None

    def get_designs(self, game):
        """Get list of all non-None designs for player's faction.

        Args:
            game: Game instance to access faction designs

        Returns:
            list: All active designs (excludes None slots)
        """
        return game.factions[game.player_faction_id].designs.get_designs()

    def _load_slot_into_editor(self, slot_index, game):
        """Load a slot's design into the editor, or reset to defaults if empty.

        Args:
            slot_index: Index of slot to load (0-63)
            game: Game instance to access faction designs
        """
        self.selected_slot = slot_index
        designs = game.factions[game.player_faction_id].designs
        design = designs.get_design(slot_index)

        if design is None:
            # Empty slot - reset to defaults
            self.dw_selected_chassis = 'infantry'
            self.dw_selected_weapon = 'hand_weapons'
            self.dw_selected_armor = 'no_armor'
            self.dw_selected_reactor = 'fission'
            self.dw_selected_ability1 = 'none'
            self.dw_selected_ability2 = 'none'
        else:
            # Load existing design (already stores IDs)
            self.dw_selected_chassis = design['chassis']
            self.dw_selected_weapon = design['weapon']
            self.dw_selected_armor = design['armor']
            self.dw_selected_reactor = design['reactor']
            self.dw_selected_ability1 = design.get('ability1', 'none')
            self.dw_selected_ability2 = design.get('ability2', 'none')

    def check_if_tech_unlocks_components(self, tech_id, tech_tree):
        """Check if a specific tech unlocks any new components.

        Args:
            tech_id: The tech ID that was just completed
            tech_tree: TechTree instance

        Returns:
            tuple: (bool, list of component types unlocked) - e.g. (True, ['weapon', 'armor'])
        """
        from game.unit_components import CHASSIS, WEAPONS, ARMOR, REACTORS, SPECIAL_ABILITIES

        unlocked = []

        # Check each component type
        for chassis in CHASSIS:
            if chassis['prereq'] == tech_id:
                unlocked.append('chassis')
                break

        for weapon in WEAPONS:
            if weapon['prereq'] == tech_id:
                unlocked.append('weapon')
                break

        for armor in ARMOR:
            if armor['prereq'] == tech_id:
                unlocked.append('armor')
                break

        for reactor in REACTORS:
            if reactor['prereq'] == tech_id:
                unlocked.append('reactor')
                break

        for ability in SPECIAL_ABILITIES:
            if ability['prereq'] == tech_id:
                unlocked.append('ability')
                break

        return (len(unlocked) > 0, unlocked)

    def rebuild_available_designs(self, tech_tree, game, completed_tech_id=None):
        """Intelligently rebuild unit designs based on what new tech unlocked.

        Only creates units that are strategically useful:
        - For new weapons: min-armor (offensive) and max-armor (defensive) variants
        - For new armor: units with best weapon
        - For new chassis: basic version with current best components
        - Follows SMAC rules: air units never get armor, combat units always do

        Args:
            tech_tree: TechTree instance to check discovered techs
            game: Game instance to access faction designs
            completed_tech_id: Optional - the tech that was just completed (for targeted generation)
        """
        from game.unit_components import CHASSIS, WEAPONS, ARMOR, REACTORS, generate_unit_name

        # Get player's faction designs
        faction_designs = game.factions[game.player_faction_id].designs
        current_designs = faction_designs.get_designs()

        print(f"DESIGN WORKSHOP: Rebuilding designs (current count: {len(current_designs)})")
        if completed_tech_id:
            print(f"  Triggered by tech: {completed_tech_id}")

        # Keep existing designs (don't reset!)
        # Generate names from component IDs for duplicate checking
        existing_names = {generate_unit_name(d['weapon'], d['chassis'], d['armor'], d['reactor'])
                          for d in current_designs}

        # Get available components
        available_chassis = [c for c in CHASSIS if c['prereq'] is None or tech_tree.has_tech(c['prereq'])]
        available_weapons = [w for w in WEAPONS if w['prereq'] is None or tech_tree.has_tech(w['prereq'])]
        available_armor = [a for a in ARMOR if a['prereq'] is None or tech_tree.has_tech(a['prereq'])]
        available_reactors = [r for r in REACTORS if r['prereq'] is None or tech_tree.has_tech(r['prereq'])]

        # Get best and worst armor for min-max strategy
        combat_armor = [a for a in available_armor if a['id'] != 'no_armor' and a['defense'] > 0]
        best_armor = max(combat_armor, key=lambda a: a['defense']) if combat_armor else None
        min_armor_obj = available_armor[0]  # No Armor
        best_reactor = available_reactors[-1] if available_reactors else REACTORS[0]

        # Separate weapons by type
        combat_weapons = [w for w in available_weapons if w['attack'] > 0]
        noncombat_weapons = [w for w in available_weapons if w['attack'] == 0]

        # Determine what to generate based on completed tech
        new_designs = []

        if not completed_tech_id:
            # Initial generation: designs already initialized in faction
            print(f"  Initial load (designs already exist)")
            return  # Don't generate anything else on initial load

        if completed_tech_id:
            # Targeted generation: only create units related to the new tech
            new_chassis = [c for c in available_chassis if c['prereq'] == completed_tech_id]
            new_weapons = [w for w in available_weapons if w['prereq'] == completed_tech_id]
            new_armor = [a for a in available_armor if a['prereq'] == completed_tech_id]

            # New weapon unlocked: create min-max variants
            for weapon in new_weapons:
                if weapon['attack'] > 0:  # Combat weapon
                    for chassis in available_chassis:
                        # Determine armor based on chassis type
                        armor_to_use = self._get_armor_for_chassis(chassis, best_armor, min_armor_obj)

                        # Min-armor variant (glass cannon)
                        if armor_to_use != min_armor_obj:  # Only if not air unit
                            design_name = generate_unit_name(weapon['id'], chassis['id'], min_armor_obj['id'])
                            if design_name not in existing_names:
                                new_designs.append({
                                    "chassis": chassis['id'],
                                    "weapon": weapon['id'],
                                    "armor": min_armor_obj['id'],
                                    "reactor": best_reactor['id'],
                                    "ability1": "none",
                                    "ability2": "none"
                                })

                        # Max-armor variant (tank) - only for ground units
                        if chassis['type'] in ['land', 'sea'] and best_armor:
                            design_name = generate_unit_name(weapon['id'], chassis['id'], best_armor['id'])
                            if design_name not in existing_names:
                                new_designs.append({
                                    "chassis": chassis['id'],
                                    "weapon": weapon['id'],
                                    "armor": best_armor['id'],
                                    "reactor": best_reactor['id'],
                                    "ability1": "none",
                                    "ability2": "none"
                                })

            # New armor unlocked: create units with best weapon
            for armor in new_armor:
                if armor['defense'] > 1:  # Not "No Armor"
                    best_weapon = max(combat_weapons, key=lambda w: w['attack']) if combat_weapons else None
                    if best_weapon:
                        for chassis in available_chassis:
                            # Only for chassis that use armor
                            if chassis['type'] in ['land', 'sea']:
                                design_name = generate_unit_name(best_weapon['id'], chassis['id'], armor['id'])
                                if design_name not in existing_names:
                                    new_designs.append({
                                        "chassis": chassis['id'],
                                        "weapon": best_weapon['id'],
                                        "armor": armor['id'],
                                        "reactor": best_reactor['id'],
                                        "ability1": "none",
                                        "ability2": "none"
                                    })

            # New chassis unlocked: create basic version
            for chassis in new_chassis:
                best_weapon = max(combat_weapons, key=lambda w: w['attack']) if combat_weapons else None
                if best_weapon:
                    armor_to_use = self._get_armor_for_chassis(chassis, best_armor, min_armor_obj)
                    design_name = generate_unit_name(best_weapon['id'], chassis['id'], armor_to_use['id'])
                    if design_name not in existing_names:
                        new_designs.append({
                            "chassis": chassis['id'],
                            "weapon": best_weapon['id'],
                            "armor": armor_to_use['id'],
                            "reactor": best_reactor['id'],
                            "ability1": "none",
                            "ability2": "none"
                        })

                # Also create colony pod version if available
                colony_weapon = next((w for w in noncombat_weapons if w['id'] == 'colony_pod'), None)
                if colony_weapon and chassis['id'] != 'missile':
                    design_name = generate_unit_name('colony_pod', chassis['id'])
                    if design_name not in existing_names:
                        new_designs.append({
                            "chassis": chassis['id'],
                            "weapon": colony_weapon['id'],
                            "armor": "no_armor",
                            "reactor": best_reactor['id'],
                            "ability1": "none",
                            "ability2": "none"
                        })

        # Add all new designs to first available empty slots
        added_count = 0
        for design in new_designs:
            design_name = generate_unit_name(design['weapon'], design['chassis'], design['armor'], design['reactor'])
            if design_name not in existing_names:
                # Add to first empty slot
                slot_index = faction_designs.add_design(design)
                if slot_index is not None:
                    existing_names.add(design_name)
                    added_count += 1

        print(f"  Added {added_count} new designs")
        print(f"  Final design count: {len(faction_designs.get_designs())}")
        if added_count > 0:
            print(f"  Added {added_count} new design variants")

    def _get_armor_for_chassis(self, chassis, best_armor, no_armor):
        """Determine appropriate armor for a chassis following SMAC rules.

        Args:
            chassis: Chassis dict
            best_armor: Best available armor dict (can be None)
            no_armor: No Armor dict

        Returns:
            Armor dict to use
        """
        # Air units never get armor
        if chassis['type'] == 'air':
            return no_armor

        # Ground and sea combat units get best armor
        if chassis['type'] in ['land', 'sea']:
            return best_armor if best_armor else no_armor

        return no_armor

    def draw_design_workshop(self, screen, game):
        """Draw the Design Workshop screen.

        Args:
            screen: Pygame screen surface to draw on
            game: Game instance for accessing tech tree and other game state
        """
        # Fill background
        screen.fill((20, 25, 30))

        screen_w = constants.SCREEN_WIDTH
        screen_h = constants.SCREEN_HEIGHT

        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("DESIGN WORKSHOP", True, (180, 220, 240))
        screen.blit(title, (screen_w // 2 - title.get_width() // 2, 20))

        # Layout constants
        panel_x = 60
        panel_y = 100
        panel_w = 300
        panel_h = 120
        panel_spacing = 20

        right_panel_x = screen_w - panel_x - panel_w

        # LEFT COLUMN PANELS
        # Chassis panel
        chassis_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        self.dw_chassis_rect = chassis_rect
        current_chassis = unit_components.get_chassis_by_id(self.dw_selected_chassis)
        self._draw_component_panel(screen, chassis_rect, "CHASSIS", current_chassis['name'])

        # Weapon panel
        weapon_rect = pygame.Rect(panel_x, panel_y + panel_h + panel_spacing, panel_w, panel_h)
        self.dw_weapon_rect = weapon_rect
        current_weapon = unit_components.get_weapon_by_id(self.dw_selected_weapon)
        self._draw_component_panel(screen, weapon_rect, "WEAPON", current_weapon['name'])

        # Armor panel
        armor_rect = pygame.Rect(panel_x, panel_y + 2 * (panel_h + panel_spacing), panel_w, panel_h)
        self.dw_armor_rect = armor_rect
        current_armor = unit_components.get_armor_by_id(self.dw_selected_armor)
        self._draw_component_panel(screen, armor_rect, "ARMOR", current_armor['name'])

        # RIGHT COLUMN PANELS
        # Reactor panel
        reactor_rect = pygame.Rect(right_panel_x, panel_y, panel_w, panel_h)
        self.dw_reactor_rect = reactor_rect
        current_reactor = unit_components.get_reactor_by_id(self.dw_selected_reactor)
        self._draw_component_panel(screen, reactor_rect, "REACTOR", current_reactor['name'])

        # Special Ability 1 panel
        special1_rect = pygame.Rect(right_panel_x, panel_y + panel_h + panel_spacing, panel_w, panel_h)
        self.dw_ability1_rect = special1_rect
        current_ability1 = unit_components.get_ability_by_id(self.dw_selected_ability1)
        self._draw_component_panel(screen, special1_rect, "SPECIAL ABILITY 1", current_ability1['name'])

        # Special Ability 2 panel
        special2_rect = pygame.Rect(right_panel_x, panel_y + 2 * (panel_h + panel_spacing), panel_w, panel_h)
        self.dw_ability2_rect = special2_rect
        current_ability2 = unit_components.get_ability_by_id(self.dw_selected_ability2)
        self._draw_component_panel(screen, special2_rect, "SPECIAL ABILITY 2", current_ability2['name'])

        # CENTER PANEL - Current Unit Stats DisplaySo
        center_panel_w = 400
        center_panel_h = 300
        center_panel_x = (screen_w - center_panel_w) // 2
        center_panel_y = panel_y
        center_panel_rect = pygame.Rect(center_panel_x, center_panel_y, center_panel_w, center_panel_h)

        # Background
        pygame.draw.rect(screen, (25, 30, 35), center_panel_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 140, 160), center_panel_rect, 3, border_radius=10)

        # Unit name - pass armor and reactor for correct SMAC naming
        unit_name = unit_components.generate_unit_name(
            self.dw_selected_weapon,
            self.dw_selected_chassis,
            self.dw_selected_armor,
            self.dw_selected_reactor
        )
        name_surf = self.font.render(unit_name, True, (200, 220, 240))
        screen.blit(name_surf, (center_panel_rect.centerx - name_surf.get_width() // 2, center_panel_y + 20))

        # Calculate total costs
        total_cost = (current_chassis['cost'] + current_weapon['cost'] +
                     current_armor['cost'] + current_reactor.get('cost', 0) +
                     current_ability1['cost'] + current_ability2['cost'])

        # Stats display
        stats_y = center_panel_y + 65
        line_height = 30

        stats_lines = [
            f"Attack: {current_weapon['attack']} ({current_weapon['mode'].title()})",
            f"Defense: {current_armor['defense']} ({current_armor['mode'].title()})",
            f"Speed: {current_chassis['speed']}",
            f"Reactor: {current_reactor['name']} (x{current_reactor['power']})",
            f"",
            f"Total Cost: {total_cost} minerals",
        ]

        # Add special abilities if not "None"
        if current_ability1['id'] != 'none':
            stats_lines.append(f"• {current_ability1['name']}")
        if current_ability2['id'] != 'none':
            stats_lines.append(f"• {current_ability2['name']}")

        for i, line in enumerate(stats_lines):
            if line:  # Skip empty lines for spacing
                color = (180, 220, 240) if "Total Cost" in line else (180, 190, 200)
                line_surf = self.small_font.render(line, True, color)
                screen.blit(line_surf, (center_panel_rect.x + 20, stats_y + i * line_height))

        # DESIGNS ARRAY AT BOTTOM - Show 64 slots in pages of 8
        designs_y = panel_y + 3 * (panel_h + panel_spacing) + 40
        designs_label = self.font.render("SAVED DESIGNS", True, (180, 220, 240))
        screen.blit(designs_label, (screen_w // 2 - designs_label.get_width() // 2, designs_y))

        # Design squares
        design_size = 80
        design_spacing = 15
        designs_start_y = designs_y + 35

        # Calculate total width needed for visible designs
        total_designs_w = self.designs_per_page * design_size + (self.designs_per_page - 1) * design_spacing
        arrow_w = 40
        arrow_spacing = 20

        # Center the entire designs section
        designs_center_x = screen_w // 2
        designs_start_x = designs_center_x - (total_designs_w + 2 * arrow_w + 2 * arrow_spacing) // 2

        # Left arrow (always enabled - loops around)
        left_arrow_rect = pygame.Rect(designs_start_x, designs_start_y + design_size // 2 - 20, arrow_w, 40)
        self.dw_left_arrow_rect = left_arrow_rect
        pygame.draw.rect(screen, COLOR_BUTTON, left_arrow_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, left_arrow_rect, 2, border_radius=6)
        arrow_text = self.font.render("<", True, COLOR_TEXT)
        screen.blit(arrow_text, (left_arrow_rect.centerx - arrow_text.get_width() // 2, left_arrow_rect.centery - 10))

        # Design squares - show 8 slots from the 64-slot array
        self.dw_design_rects = []
        designs_x = designs_start_x + arrow_w + arrow_spacing

        for i in range(self.designs_per_page):
            slot_idx = self.design_scroll_offset + i
            if slot_idx < 64:  # Always show up to 64 slots
                design_rect = pygame.Rect(designs_x + i * (design_size + design_spacing), designs_start_y,
                                         design_size, design_size)
                self.dw_design_rects.append((design_rect, slot_idx))

                faction_designs = game.factions[game.player_faction_id].designs
                design = faction_designs.get_design(slot_idx)
                is_hover = design_rect.collidepoint(pygame.mouse.get_pos())
                is_selected = (slot_idx == self.selected_slot)

                # Empty slot or filled slot
                if design is None:
                    # Empty slot
                    bg_color = (30, 35, 40) if not is_hover else (40, 45, 50)
                    border_color = (255, 255, 255) if is_selected else (80, 90, 100)
                    border_width = 3 if is_selected else 2
                    pygame.draw.rect(screen, bg_color, design_rect, border_radius=6)
                    pygame.draw.rect(screen, border_color, design_rect, border_width, border_radius=6)

                    # Show slot number
                    slot_text = self.small_font.render(f"#{slot_idx + 1}", True, (100, 110, 120))
                    screen.blit(slot_text, (design_rect.centerx - slot_text.get_width() // 2,
                                          design_rect.centery - 8))
                else:
                    # Filled slot
                    bg_color = (50, 60, 70) if is_hover else (40, 45, 50)
                    border_color = (255, 255, 255) if is_selected else (100, 140, 160)
                    border_width = 3 if is_selected else 2
                    pygame.draw.rect(screen, bg_color, design_rect, border_radius=6)
                    pygame.draw.rect(screen, border_color, design_rect, border_width, border_radius=6)

                    # Generate design name from components
                    from game.unit_components import generate_unit_name
                    design_name = generate_unit_name(
                        design['weapon'], design['chassis'], design['armor'], design['reactor']
                    )

                    # Design name (wrapped)
                    name_lines = self._wrap_text(design_name, design_size - 10, self.small_font)
                    for j, line in enumerate(name_lines[:2]):  # Max 2 lines (leave room for stats)
                        line_surf = self.small_font.render(line, True, COLOR_TEXT)
                        screen.blit(line_surf, (design_rect.x + 5, design_rect.y + 10 + j * 18))

                    # Unit stats (weapon-armor-speed) below name - look up from IDs
                    weapon_data = unit_components.get_weapon_by_id(design['weapon'])
                    armor_data = unit_components.get_armor_by_id(design['armor'])
                    chassis_data = unit_components.get_chassis_by_id(design['chassis'])
                    weapon_power = weapon_data['attack'] if weapon_data else 0
                    armor_defense = armor_data['defense'] if armor_data else 0
                    chassis_speed = chassis_data['speed'] if chassis_data else 1
                    stats_text = f"{weapon_power}-{armor_defense}-{chassis_speed}"
                    stats_surf = self.small_font.render(stats_text, True, (200, 220, 100))
                    screen.blit(stats_surf, (design_rect.centerx - stats_surf.get_width() // 2,
                                           design_rect.bottom - 20))

        # Right arrow (always enabled - loops around)
        right_arrow_rect = pygame.Rect(designs_x + self.designs_per_page * (design_size + design_spacing),
                                       designs_start_y + design_size // 2 - 20, arrow_w, 40)
        self.dw_right_arrow_rect = right_arrow_rect
        pygame.draw.rect(screen, COLOR_BUTTON, right_arrow_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, right_arrow_rect, 2, border_radius=6)
        arrow_text = self.font.render(">", True, COLOR_TEXT)
        screen.blit(arrow_text, (right_arrow_rect.centerx - arrow_text.get_width() // 2, right_arrow_rect.centery - 10))

        # BOTTOM BUTTONS
        button_y = designs_start_y + design_size + 30
        button_w = 120
        button_h = 45
        button_spacing_x = 15

        # Calculate total width for 6 buttons
        total_buttons_w = 6 * button_w + 5 * button_spacing_x
        button_start_x = screen_w // 2 - total_buttons_w // 2

        buttons = ["Apply", "Done", "Rename", "Obsolete", "Disband", "Cancel"]
        button_rects = []

        for i, label in enumerate(buttons):
            btn_rect = pygame.Rect(button_start_x + i * (button_w + button_spacing_x), button_y, button_w, button_h)
            is_hover = btn_rect.collidepoint(pygame.mouse.get_pos())

            # Disable Rename button if selected slot is empty
            current_design = game.factions[game.player_faction_id].designs.get_design(self.selected_slot)
            is_disabled = (label == "Rename" and current_design is None)

            if is_disabled:
                pygame.draw.rect(screen, (60, 60, 60), btn_rect, border_radius=6)
                pygame.draw.rect(screen, (80, 80, 80), btn_rect, 2, border_radius=6)
                btn_text = self.font.render(label, True, (100, 100, 100))
            else:
                pygame.draw.rect(screen, COLOR_BUTTON_HOVER if is_hover else COLOR_BUTTON, btn_rect, border_radius=6)
                pygame.draw.rect(screen, COLOR_BUTTON_HIGHLIGHT if is_hover else COLOR_BUTTON_BORDER, btn_rect, 2, border_radius=6)
                btn_text = self.font.render(label, True, COLOR_TEXT)

            screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width() // 2, btn_rect.centery - 10))

            button_rects.append(btn_rect)

        # Store button rects
        self.dw_apply_rect = button_rects[0]
        self.dw_done_rect = button_rects[1]
        self.dw_rename_rect = button_rects[2]
        self.dw_obsolete_rect = button_rects[3]
        self.dw_disband_rect = button_rects[4]
        self.dw_cancel_rect = button_rects[5]

        # Draw component selection modal if a panel is being edited
        if self.dw_editing_panel:
            self._draw_component_selection(screen, game)

        # Draw rename popup if open
        if self.rename_popup_open:
            self._draw_rename_popup(screen)

    def _draw_component_panel(self, screen, rect, title, value):
        """Draw a component selection panel.

        Args:
            screen: Pygame screen surface to draw on
            rect: Rectangle defining the panel area
            title: Panel title string
            value: Current component value to display
        """
        # Highlight if being edited
        is_editing = (
            (title == "CHASSIS" and self.dw_editing_panel == 'chassis') or
            (title == "WEAPON" and self.dw_editing_panel == 'weapon') or
            (title == "ARMOR" and self.dw_editing_panel == 'armor') or
            (title == "REACTOR" and self.dw_editing_panel == 'reactor') or
            (title == "SPECIAL ABILITY 1" and self.dw_editing_panel == 'ability1') or
            (title == "SPECIAL ABILITY 2" and self.dw_editing_panel == 'ability2')
        )

        border_color = (255, 200, 100) if is_editing else (100, 120, 140)
        pygame.draw.rect(screen, (35, 40, 45), rect, border_radius=8)
        pygame.draw.rect(screen, border_color, rect, 3 if is_editing else 2, border_radius=8)

        # Title
        title_surf = self.small_font.render(title, True, (150, 180, 200))
        screen.blit(title_surf, (rect.x + 10, rect.y + 10))

        # Current value
        value_surf = self.font.render(value, True, COLOR_TEXT)
        screen.blit(value_surf, (rect.x + 10, rect.y + 45))

        # Get stats based on panel type
        stats_text = ""
        if title == "CHASSIS":
            chassis = unit_components.get_chassis_by_id(self.dw_selected_chassis)
            stats_text = f"Speed: {chassis['speed']}, Cost: {chassis['cost']}"
        elif title == "WEAPON":
            weapon = unit_components.get_weapon_by_id(self.dw_selected_weapon)
            mode_abbrev = weapon['mode'][0].upper() if weapon['mode'] != 'noncombat' else 'NC'
            stats_text = f"Atk: {weapon['attack']}, Mode: {mode_abbrev}, Cost: {weapon['cost']}"
        elif title == "ARMOR":
            armor = unit_components.get_armor_by_id(self.dw_selected_armor)
            mode_abbrev = armor['mode'][0].upper() if armor['mode'] != 'psi' else 'Psi'
            stats_text = f"Def: {armor['defense']}, Mode: {mode_abbrev}, Cost: {armor['cost']}"
        elif title == "REACTOR":
            reactor = unit_components.get_reactor_by_id(self.dw_selected_reactor)
            stats_text = f"Power: {reactor['power']}"
        elif title == "SPECIAL ABILITY 1":
            ability = unit_components.get_ability_by_id(self.dw_selected_ability1)
            stats_text = f"Cost: {ability['cost']}"
        elif title == "SPECIAL ABILITY 2":
            ability = unit_components.get_ability_by_id(self.dw_selected_ability2)
            stats_text = f"Cost: {ability['cost']}"

        # Stats (wrap to 2 lines if needed for weapons/armor)
        if title in ["WEAPON", "ARMOR"] and len(stats_text) > 30:
            # Split into 2 lines
            parts = stats_text.split(', ')
            line1 = parts[0] + ', ' + parts[1]
            line2 = parts[2] if len(parts) > 2 else ''
            stats_surf1 = self.small_font.render(line1, True, (180, 190, 200))
            screen.blit(stats_surf1, (rect.x + 10, rect.y + 75))
            if line2:
                stats_surf2 = self.small_font.render(line2, True, (180, 190, 200))
                screen.blit(stats_surf2, (rect.x + 10, rect.y + 90))
        else:
            stats_surf = self.small_font.render(stats_text, True, (180, 190, 200))
            screen.blit(stats_surf, (rect.x + 10, rect.y + 80))

    def _draw_component_selection(self, screen, game):
        """Draw component selection modal overlay.

        Args:
            screen: Pygame screen surface to draw on
            game: Game instance for accessing tech tree
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Selection box
        box_w = 700
        box_h = 600
        box_x = (constants.SCREEN_WIDTH - box_w) // 2
        box_y = (constants.SCREEN_HEIGHT - box_h) // 2

        pygame.draw.rect(screen, (30, 35, 40), pygame.Rect(box_x, box_y, box_w, box_h), border_radius=10)
        pygame.draw.rect(screen, (150, 180, 200), pygame.Rect(box_x, box_y, box_w, box_h), 3, border_radius=10)

        # Title
        title_text = self.font.render(f"SELECT {self.dw_editing_panel.upper()}", True, (180, 220, 240))
        screen.blit(title_text, (box_x + box_w // 2 - title_text.get_width() // 2, box_y + 20))

        # Get components list based on editing panel
        if self.dw_editing_panel == 'chassis':
            all_components = unit_components.CHASSIS
        elif self.dw_editing_panel == 'weapon':
            all_components = unit_components.WEAPONS
        elif self.dw_editing_panel == 'armor':
            all_components = unit_components.ARMOR
        elif self.dw_editing_panel == 'reactor':
            all_components = unit_components.REACTORS
        elif self.dw_editing_panel in ['ability1', 'ability2']:
            all_components = unit_components.SPECIAL_ABILITIES
        else:
            all_components = []

        # Filter components by tech prerequisites
        player_tech_tree = game.factions[game.player_faction_id].tech_tree
        components = [c for c in all_components if unit_components.is_component_available(c, player_tech_tree)]

        # Draw components
        self.dw_component_selection_rects = []

        # Grid layout for chassis, weapons, armor, reactor
        if self.dw_editing_panel in ['chassis', 'weapon', 'armor', 'reactor']:
            # Reactor uses 4 columns, others use 5
            grid_cols = 4 if self.dw_editing_panel == 'reactor' else 5
            square_size = 105
            square_spacing = 12
            start_x = box_x + 30
            start_y = box_y + 70

            for i, component in enumerate(components):
                row = i // grid_cols
                col = i % grid_cols

                square_x = start_x + col * (square_size + square_spacing)
                square_y = start_y + row * (square_size + square_spacing)

                square_rect = pygame.Rect(square_x, square_y, square_size, square_size)
                self.dw_component_selection_rects.append((square_rect, component))

                # Highlight on hover
                is_hover = square_rect.collidepoint(pygame.mouse.get_pos())
                bg_color = (50, 60, 70) if is_hover else (40, 45, 50)
                pygame.draw.rect(screen, bg_color, square_rect, border_radius=5)
                pygame.draw.rect(screen, (100, 120, 140), square_rect, 2, border_radius=5)

                # Component name (wrapped)
                name_lines = self._wrap_text(component['name'], square_size - 10, self.small_font)
                for j, line in enumerate(name_lines[:2]):  # Max 2 lines
                    line_surf = self.small_font.render(line, True, COLOR_TEXT)
                    screen.blit(line_surf, (square_x + 5, square_y + 5 + j * 16))

                # Component key stat
                if self.dw_editing_panel == 'chassis':
                    stat_text = f"Spd: {component['speed']}"
                elif self.dw_editing_panel == 'weapon':
                    stat_text = f"Atk: {component['attack']}"
                    # Show mode
                    mode_abbrev = component['mode'][0].upper() if component['mode'] != 'noncombat' else 'NC'
                    mode_surf = self.small_font.render(f"({mode_abbrev})", True, (180, 200, 200))
                    screen.blit(mode_surf, (square_x + 5, square_y + 68))
                elif self.dw_editing_panel == 'armor':
                    stat_text = f"Def: {component['defense']}"
                    # Show mode
                    mode_abbrev = component['mode'][0].upper() if component['mode'] != 'psi' else 'Psi'
                    mode_surf = self.small_font.render(f"({mode_abbrev})", True, (180, 200, 200))
                    screen.blit(mode_surf, (square_x + 5, square_y + 68))
                elif self.dw_editing_panel == 'reactor':
                    stat_text = f"Pwr: {component['power']}"
                else:
                    stat_text = ""

                stat_surf = self.small_font.render(stat_text, True, (150, 200, 150))
                screen.blit(stat_surf, (square_x + 5, square_y + 50))

        # List layout for special abilities only
        else:
            item_height = 50
            start_y = box_y + 70
            max_visible = 9

            # Apply scroll offset for special abilities
            visible_components = components[self.dw_ability_scroll_offset:self.dw_ability_scroll_offset + max_visible]

            # Draw scroll arrows if needed
            if len(components) > max_visible:
                # Up arrow
                up_arrow_rect = pygame.Rect(box_x + box_w - 50, start_y - 10, 30, 30)
                can_scroll_up = self.dw_ability_scroll_offset > 0
                arrow_color = COLOR_BUTTON if can_scroll_up else (60, 60, 60)
                pygame.draw.rect(screen, arrow_color, up_arrow_rect, border_radius=4)
                pygame.draw.rect(screen, COLOR_BUTTON_BORDER, up_arrow_rect, 2, border_radius=4)
                arrow_text = self.font.render("^", True, COLOR_TEXT if can_scroll_up else (100, 100, 100))
                screen.blit(arrow_text, (up_arrow_rect.centerx - arrow_text.get_width() // 2, up_arrow_rect.centery - 10))
                self.dw_ability_up_arrow = up_arrow_rect

                # Down arrow
                down_arrow_rect = pygame.Rect(box_x + box_w - 50, start_y + max_visible * item_height, 30, 30)
                can_scroll_down = self.dw_ability_scroll_offset + max_visible < len(components)
                arrow_color = COLOR_BUTTON if can_scroll_down else (60, 60, 60)
                pygame.draw.rect(screen, arrow_color, down_arrow_rect, border_radius=4)
                pygame.draw.rect(screen, COLOR_BUTTON_BORDER, down_arrow_rect, 2, border_radius=4)
                arrow_text = self.font.render("v", True, COLOR_TEXT if can_scroll_down else (100, 100, 100))
                screen.blit(arrow_text, (down_arrow_rect.centerx - arrow_text.get_width() // 2, down_arrow_rect.centery - 10))
                self.dw_ability_down_arrow = down_arrow_rect

            for i, component in enumerate(visible_components):
                item_rect = pygame.Rect(box_x + 20, start_y + i * item_height, box_w - 80, item_height - 5)
                self.dw_component_selection_rects.append((item_rect, component))

                # Highlight on hover
                is_hover = item_rect.collidepoint(pygame.mouse.get_pos())
                bg_color = (50, 60, 70) if is_hover else (40, 45, 50)
                pygame.draw.rect(screen, bg_color, item_rect, border_radius=5)
                pygame.draw.rect(screen, (100, 120, 140), item_rect, 2, border_radius=5)

                # Component name
                name_surf = self.font.render(component['name'], True, COLOR_TEXT)
                screen.blit(name_surf, (item_rect.x + 10, item_rect.y + 5))

                # Component stats - only special abilities use this section now
                stats = f"Cost: {component['cost']} - {component['description']}"
                stats_surf = self.small_font.render(stats, True, (180, 190, 200))
                screen.blit(stats_surf, (item_rect.x + 10, item_rect.y + 25))

        # Cancel button
        cancel_btn_w = 100
        cancel_btn_h = 40
        cancel_btn_x = box_x + box_w // 2 - cancel_btn_w // 2
        cancel_btn_y = box_y + box_h - 60
        cancel_btn_rect = pygame.Rect(cancel_btn_x, cancel_btn_y, cancel_btn_w, cancel_btn_h)

        is_cancel_hover = cancel_btn_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if is_cancel_hover else COLOR_BUTTON, cancel_btn_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, cancel_btn_rect, 2, border_radius=6)
        cancel_text = self.font.render("Cancel", True, COLOR_TEXT)
        screen.blit(cancel_text, (cancel_btn_rect.centerx - cancel_text.get_width() // 2, cancel_btn_rect.centery - 10))

        self.dw_component_cancel_rect = cancel_btn_rect

    def _draw_rename_popup(self, screen):
        """Draw the rename popup with text input.

        Args:
            screen: Pygame screen surface to draw on
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Popup box
        box_w = 500
        box_h = 200
        box_x = (constants.SCREEN_WIDTH - box_w) // 2
        box_y = (constants.SCREEN_HEIGHT - box_h) // 2

        pygame.draw.rect(screen, (30, 35, 40), pygame.Rect(box_x, box_y, box_w, box_h), border_radius=10)
        pygame.draw.rect(screen, (150, 180, 200), pygame.Rect(box_x, box_y, box_w, box_h), 3, border_radius=10)

        # Title
        title_text = self.font.render("RENAME UNIT", True, (180, 220, 240))
        screen.blit(title_text, (box_x + box_w // 2 - title_text.get_width() // 2, box_y + 20))

        # Text input box
        input_box_w = 440
        input_box_h = 40
        input_box_x = box_x + (box_w - input_box_w) // 2
        input_box_y = box_y + 70
        input_box_rect = pygame.Rect(input_box_x, input_box_y, input_box_w, input_box_h)

        pygame.draw.rect(screen, (40, 45, 50), input_box_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 140, 160), input_box_rect, 2, border_radius=5)

        # Text input
        text_surf = self.font.render(self.rename_text_input, True, COLOR_TEXT)

        # If text is selected, draw a blue highlight behind it
        if self.rename_text_selected and self.rename_text_input:
            highlight_rect = pygame.Rect(input_box_x + 10, input_box_y + 8, text_surf.get_width(), text_surf.get_height())
            pygame.draw.rect(screen, (60, 100, 180), highlight_rect)

        screen.blit(text_surf, (input_box_x + 10, input_box_y + 8))

        # Cursor (blinking) - only show if text is NOT selected
        if not self.rename_text_selected:
            import time
            if int(time.time() * 2) % 2 == 0:  # Blink every 0.5 seconds
                cursor_x = input_box_x + 10 + text_surf.get_width()
                pygame.draw.line(screen, COLOR_TEXT, (cursor_x, input_box_y + 8), (cursor_x, input_box_y + 32), 2)

        # OK and Cancel buttons
        button_w = 100
        button_h = 40
        button_y = box_y + box_h - 60
        ok_x = box_x + box_w // 2 - button_w - 10
        cancel_x = box_x + box_w // 2 + 10

        # OK button
        ok_rect = pygame.Rect(ok_x, button_y, button_w, button_h)
        self.dw_rename_ok_rect = ok_rect
        is_ok_hover = ok_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if is_ok_hover else COLOR_BUTTON, ok_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, ok_rect, 2, border_radius=6)
        ok_text = self.font.render("OK", True, COLOR_TEXT)
        screen.blit(ok_text, (ok_rect.centerx - ok_text.get_width() // 2, ok_rect.centery - 10))

        # Cancel button
        cancel_rect = pygame.Rect(cancel_x, button_y, button_w, button_h)
        self.dw_rename_cancel_rect = cancel_rect
        is_cancel_hover = cancel_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if is_cancel_hover else COLOR_BUTTON, cancel_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, cancel_rect, 2, border_radius=6)
        cancel_text = self.font.render("Cancel", True, COLOR_TEXT)
        screen.blit(cancel_text, (cancel_rect.centerx - cancel_text.get_width() // 2, cancel_rect.centery - 10))

    def handle_design_workshop_click(self, pos, game):
        """Handle clicks in the Design Workshop screen.

        Args:
            pos: Mouse click position tuple (x, y)
            game: Game instance to access faction designs

        Returns:
            'close' if should exit the screen, None otherwise
        """
        # If rename popup is open, handle those clicks first
        if self.rename_popup_open:
            # Check OK button
            if hasattr(self, 'dw_rename_ok_rect') and self.dw_rename_ok_rect and self.dw_rename_ok_rect.collidepoint(pos):
                # Rename not supported - names are auto-generated from components
                self.rename_popup_open = False
                self.rename_text_selected = False
                return None

            # Check Cancel button
            if hasattr(self, 'dw_rename_cancel_rect') and self.dw_rename_cancel_rect and self.dw_rename_cancel_rect.collidepoint(pos):
                self.rename_popup_open = False
                self.rename_text_selected = False
                return None

            # Click in input box - deselect text
            input_box_x = (constants.SCREEN_WIDTH - 500) // 2 + 30
            input_box_y = (constants.SCREEN_HEIGHT - 200) // 2 + 70
            input_box_rect = pygame.Rect(input_box_x, input_box_y, 440, 40)
            if input_box_rect.collidepoint(pos):
                self.rename_text_selected = False
                return None

            # Click outside popup - ignore
            return None

        # If component selection modal is open, handle those clicks first
        if self.dw_editing_panel:
            # Check scroll arrows for special abilities
            if self.dw_editing_panel in ['ability1', 'ability2']:
                if hasattr(self, 'dw_ability_up_arrow') and self.dw_ability_up_arrow and self.dw_ability_up_arrow.collidepoint(pos):
                    if self.dw_ability_scroll_offset > 0:
                        self.dw_ability_scroll_offset -= 1
                    return None
                if hasattr(self, 'dw_ability_down_arrow') and self.dw_ability_down_arrow and self.dw_ability_down_arrow.collidepoint(pos):
                    max_scroll = len(unit_components.SPECIAL_ABILITIES) - 9
                    if self.dw_ability_scroll_offset < max_scroll:
                        self.dw_ability_scroll_offset += 1
                    return None

            # Check cancel button in modal
            if hasattr(self, 'dw_component_cancel_rect') and self.dw_component_cancel_rect and self.dw_component_cancel_rect.collidepoint(pos):
                self.dw_editing_panel = None
                self.dw_ability_scroll_offset = 0
                return None

            # Check component selection
            if hasattr(self, 'dw_component_selection_rects'):
                for rect, component in self.dw_component_selection_rects:
                    if rect.collidepoint(pos):
                        # Select this component
                        if self.dw_editing_panel == 'chassis':
                            self.dw_selected_chassis = component['id']
                        elif self.dw_editing_panel == 'weapon':
                            self.dw_selected_weapon = component['id']
                        elif self.dw_editing_panel == 'armor':
                            self.dw_selected_armor = component['id']
                        elif self.dw_editing_panel == 'reactor':
                            self.dw_selected_reactor = component['id']
                        elif self.dw_editing_panel == 'ability1':
                            self.dw_selected_ability1 = component['id']
                        elif self.dw_editing_panel == 'ability2':
                            self.dw_selected_ability2 = component['id']
                        self.dw_editing_panel = None
                        self.dw_ability_scroll_offset = 0
                        return None

            # Click outside modal - close it
            return None

        # Check Done button
        if hasattr(self, 'dw_done_rect') and self.dw_done_rect.collidepoint(pos):
            self.design_workshop_open = False
            return 'close'

        # Check Rename button
        if hasattr(self, 'dw_rename_rect') and self.dw_rename_rect.collidepoint(pos):
            # Only open if selected slot has a design
            faction_designs = game.factions[game.player_faction_id].designs
            current_design = faction_designs.get_design(self.selected_slot)
            if current_design is not None:
                # Names are auto-generated, but we can show the current name
                from game.unit_components import generate_unit_name
                self.rename_text_input = generate_unit_name(
                    current_design['weapon'],
                    current_design['chassis'],
                    current_design['armor'],
                    current_design['reactor']
                )
                self.rename_text_selected = True  # Text starts selected
                self.rename_popup_open = True
            return None

        # Check Cancel button
        if hasattr(self, 'dw_cancel_rect') and self.dw_cancel_rect.collidepoint(pos):
            self.design_workshop_open = False
            return 'close'

        # Check component panel clicks to open selection modal
        if hasattr(self, 'dw_chassis_rect') and self.dw_chassis_rect and self.dw_chassis_rect.collidepoint(pos):
            self.dw_editing_panel = 'chassis'
            return None

        if hasattr(self, 'dw_weapon_rect') and self.dw_weapon_rect and self.dw_weapon_rect.collidepoint(pos):
            self.dw_editing_panel = 'weapon'
            return None

        if hasattr(self, 'dw_armor_rect') and self.dw_armor_rect and self.dw_armor_rect.collidepoint(pos):
            self.dw_editing_panel = 'armor'
            return None

        if hasattr(self, 'dw_reactor_rect') and self.dw_reactor_rect and self.dw_reactor_rect.collidepoint(pos):
            self.dw_editing_panel = 'reactor'
            return None

        if hasattr(self, 'dw_ability1_rect') and self.dw_ability1_rect and self.dw_ability1_rect.collidepoint(pos):
            self.dw_editing_panel = 'ability1'
            return None

        if hasattr(self, 'dw_ability2_rect') and self.dw_ability2_rect and self.dw_ability2_rect.collidepoint(pos):
            self.dw_editing_panel = 'ability2'
            return None

        # Check Apply button - save current design to selected slot
        if hasattr(self, 'dw_apply_rect') and self.dw_apply_rect.collidepoint(pos):
            from game.unit_components import CHASSIS, WEAPONS, ARMOR, REACTORS, generate_unit_name

            # Find the components for selected IDs
            chassis_obj = None
            weapon_obj = None
            armor_obj = None
            reactor_obj = None

            for c in CHASSIS:
                if c['id'] == self.dw_selected_chassis:
                    chassis_obj = c
                    break

            for w in WEAPONS:
                if w['id'] == self.dw_selected_weapon:
                    weapon_obj = w
                    break

            for a in ARMOR:
                if a['id'] == self.dw_selected_armor:
                    armor_obj = a
                    break

            for r in REACTORS:
                if r['id'] == self.dw_selected_reactor:
                    reactor_obj = r
                    break

            # Create the design dict (store component IDs)
            new_design = {
                "chassis": self.dw_selected_chassis,
                "weapon": self.dw_selected_weapon,
                "armor": self.dw_selected_armor,
                "reactor": self.dw_selected_reactor,
                "ability1": self.dw_selected_ability1,
                "ability2": self.dw_selected_ability2
            }

            # Generate name for logging
            design_name = generate_unit_name(
                self.dw_selected_weapon,
                self.dw_selected_chassis,
                self.dw_selected_armor,
                self.dw_selected_reactor
            )

            # Save to the currently selected slot
            faction_designs = game.factions[game.player_faction_id].designs
            faction_designs.set_design(self.selected_slot, new_design)
            print(f"DESIGN WORKSHOP: Saved design '{design_name}' to slot {self.selected_slot}")

            # Move to next empty slot for convenience
            next_empty = faction_designs.find_first_empty_slot()
            self._load_slot_into_editor(next_empty, game)

            return None

        # Check Obsolete button (placeholder - does nothing for now)
        if hasattr(self, 'dw_obsolete_rect') and self.dw_obsolete_rect.collidepoint(pos):
            return None

        # Check Disband button (placeholder - does nothing for now)
        if hasattr(self, 'dw_disband_rect') and self.dw_disband_rect.collidepoint(pos):
            return None

        # Check left arrow (loops around)
        if hasattr(self, 'dw_left_arrow_rect') and self.dw_left_arrow_rect.collidepoint(pos):
            self.design_scroll_offset -= self.designs_per_page
            if self.design_scroll_offset < 0:
                # Wrap to last page
                self.design_scroll_offset = 64 - self.designs_per_page
            return None

        # Check right arrow (loops around)
        if hasattr(self, 'dw_right_arrow_rect') and self.dw_right_arrow_rect.collidepoint(pos):
            self.design_scroll_offset += self.designs_per_page
            if self.design_scroll_offset >= 64:
                # Wrap to first page
                self.design_scroll_offset = 0
            return None

        # Check design squares - clicking a slot selects it and loads it into editor
        if hasattr(self, 'dw_design_rects'):
            for rect, slot_idx in self.dw_design_rects:
                if rect.collidepoint(pos):
                    # Load this slot into the editor
                    self._load_slot_into_editor(slot_idx, game)
                    return None

        return None

    def handle_design_workshop_keypress(self, event):
        """Handle keyboard input for the design workshop (mainly for rename popup).

        Args:
            event: Pygame KEYDOWN event

        Returns:
            bool: True if event was handled, False otherwise
        """
        if self.rename_popup_open:
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                # Rename not supported - names are auto-generated
                self.rename_popup_open = False
                self.rename_text_selected = False
                return True
            elif event.key == pygame.K_ESCAPE:
                # Escape key - cancel
                self.rename_popup_open = False
                self.rename_text_selected = False
                return True
            elif event.key == pygame.K_BACKSPACE:
                # Backspace - if text is selected, clear it all; otherwise delete last char
                if self.rename_text_selected:
                    self.rename_text_input = ""
                    self.rename_text_selected = False
                else:
                    self.rename_text_input = self.rename_text_input[:-1]
                return True
            elif event.unicode and len(self.rename_text_input) < 50:  # Max 50 characters
                # If text is selected, replace it with new character
                if self.rename_text_selected:
                    self.rename_text_input = event.unicode
                    self.rename_text_selected = False
                else:
                    # Add typed character
                    self.rename_text_input += event.unicode
                return True
            return True  # Consume all events when popup is open

        return False

    def _wrap_text(self, text, max_width, font):
        """Wrap text to fit within max_width.

        Args:
            text: String to wrap
            max_width: Maximum width in pixels
            font: Pygame font to use for measuring text

        Returns:
            List of wrapped text lines
        """
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines
