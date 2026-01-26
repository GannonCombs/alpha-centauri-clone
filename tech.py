# tech.py
"""Technology tree system based on Alpha Centauri alpha.txt.

Technologies have prerequisites and unlock units, facilities, and abilities.
Players accumulate research points each turn to discover new technologies.
"""

class TechTree:
    """Manages the technology tree and research progress.

    Based on the authentic SMAC tech tree from alpha.txt (lines 255-344).
    Each tech has prerequisites that must be discovered first.

    Attributes:
        technologies (dict): All technologies with prereqs and costs
        discovered_techs (set): Set of discovered tech IDs
        current_research (str): Tech ID currently being researched
        research_accumulated (int): Research points toward current tech
        research_per_turn (int): Research points gained each turn
    """

    def __init__(self):
        """Initialize the tech tree with all SMAC technologies."""
        self.technologies = self._build_tech_tree()
        self.discovered_techs = set()
        self.current_research = None  # Player chooses what to research
        self.research_accumulated = 0
        self.research_per_turn = 2  # Base research rate (will scale with labs)

    def _build_tech_tree(self):
        """Build the complete SMAC technology tree.

        Returns:
            dict: Technology database {id: {name, prereq1, prereq2, cost, category, ...}}
        """
        # Based on alpha.txt lines 255-344
        # Format: Name, id, ai-mil, ai-tech, ai-infra, ai-colonize, preq(1), preq(2), flags
        # Categories: explore (green), discover (gray), build (yellow), conquer (red)
        techs = {}

        # Tier 1: Starting technologies (no prerequisites)
        techs['Biogen'] = {'name': 'Biogenetics', 'prereq1': None, 'prereq2': None, 'cost': 10, 'category': 'discover'}  # 0,3,2,2 - tech highest
        techs['Indust'] = {'name': 'Industrial Base', 'prereq1': None, 'prereq2': None, 'cost': 10, 'category': 'build'}  # 2,1,3,0 - infra highest
        techs['InfNet'] = {'name': 'Information Networks', 'prereq1': None, 'prereq2': None, 'cost': 10, 'category': 'discover'}  # 0,3,2,1 - tech highest
        techs['Physic'] = {'name': 'Applied Physics', 'prereq1': None, 'prereq2': None, 'cost': 10, 'category': 'conquer'}  # 4,2,1,0 - mil highest
        techs['Psych'] = {'name': 'Social Psych', 'prereq1': None, 'prereq2': None, 'cost': 10, 'category': 'build'}  # 0,1,3,2 - infra highest
        techs['Mobile'] = {'name': 'Doctrine: Mobility', 'prereq1': None, 'prereq2': None, 'cost': 10, 'category': 'explore'}  # 2,0,0,3 - colonize highest
        techs['Ecology'] = {'name': 'Centauri Ecology', 'prereq1': None, 'prereq2': None, 'cost': 10, 'category': 'explore'}  # 0,1,2,3 - colonize highest

        # Tier 2: Early technologies
        techs['OptComp'] = {'name': 'Optical Computers', 'prereq1': 'Physic', 'prereq2': 'Poly', 'cost': 20, 'category': 'discover'}  # 2,4,1,0
        techs['Poly'] = {'name': 'Polymorphic Software', 'prereq1': 'Indust', 'prereq2': 'InfNet', 'cost': 20, 'category': 'discover'}  # 2,3,1,0 - tech highest
        techs['Chemist'] = {'name': 'High Energy Chemistry', 'prereq1': 'Indust', 'prereq2': 'Physic', 'cost': 20, 'category': 'conquer'}  # 3,1,2,0
        techs['DocFlex'] = {'name': 'Doctrine: Flexibility', 'prereq1': 'Mobile', 'prereq2': None, 'cost': 15, 'category': 'explore'}  # 2,0,1,4
        techs['EthCalc'] = {'name': 'Ethical Calculus', 'prereq1': 'Psych', 'prereq2': None, 'cost': 15, 'category': 'build'}  # 0,1,3,3 (infra and colonize tied, choosing build for thematic fit)
        techs['IndEcon'] = {'name': 'Industrial Economics', 'prereq1': 'Indust', 'prereq2': None, 'cost': 15, 'category': 'build'}  # 0,0,5,2
        techs['Gene'] = {'name': 'Gene Splicing', 'prereq1': 'Biogen', 'prereq2': 'EthCalc', 'cost': 20, 'category': 'build'}  # 0,2,4,3
        techs['PlaNets'] = {'name': 'Planetary Networks', 'prereq1': 'InfNet', 'prereq2': None, 'cost': 15, 'category': 'discover'}  # 0,4,3,1
        techs['DocLoy'] = {'name': 'Doctrine: Loyalty', 'prereq1': 'Mobile', 'prereq2': 'Psych', 'cost': 20, 'category': 'conquer'}  # 3,0,2,2
        techs['Brain'] = {'name': 'Secrets of the Human Brain', 'prereq1': 'Psych', 'prereq2': 'Biogen', 'cost': 25, 'category': 'discover'}  # 1,5,0,3
        techs['EcoEng'] = {'name': 'Ecological Engineering', 'prereq1': 'Ecology', 'prereq2': 'Gene', 'cost': 25, 'category': 'explore'}  # 0,0,3,4

        # Tier 3: Mid-game technologies
        techs['Super'] = {'name': 'Superconductor', 'prereq1': 'OptComp', 'prereq2': 'Indust', 'cost': 25, 'category': 'conquer'}  # 4,2,0,0
        techs['Subat'] = {'name': 'Advanced Subatomic Theory', 'prereq1': 'Chemist', 'prereq2': 'Poly', 'cost': 25, 'category': 'discover'}  # 2,3,2,0
        techs['IndAuto'] = {'name': 'Industrial Automation', 'prereq1': 'IndEcon', 'prereq2': 'PlaNets', 'cost': 25, 'category': 'build'}  # 0,1,4,3
        techs['Chaos'] = {'name': 'Nonlinear Mathematics', 'prereq1': 'Physic', 'prereq2': 'InfNet', 'cost': 25, 'category': 'conquer'}  # 4,3,0,0
        techs['MilAlg'] = {'name': 'Advanced Military Algorithms', 'prereq1': 'DocFlex', 'prereq2': 'OptComp', 'cost': 25, 'category': 'conquer'}  # 3,0,1,2
        techs['Fossil'] = {'name': 'Synthetic Fossil Fuels', 'prereq1': 'Chemist', 'prereq2': 'Gene', 'cost': 25, 'category': 'explore'}  # 1,0,2,4
        techs['DocAir'] = {'name': 'Doctrine: Air Power', 'prereq1': 'Fossil', 'prereq2': 'DocFlex', 'cost': 30, 'category': 'explore'}  # 3,0,3,4
        techs['DocInit'] = {'name': 'Doctrine: Initiative', 'prereq1': 'DocFlex', 'prereq2': 'IndAuto', 'cost': 30, 'category': 'explore'}  # 2,0,0,4
        techs['Integ'] = {'name': 'Intellectual Integrity', 'prereq1': 'EthCalc', 'prereq2': 'DocLoy', 'cost': 30, 'category': 'explore'}  # 0,1,3,4
        techs['Cyber'] = {'name': 'Cyberethics', 'prereq1': 'PlaNets', 'prereq2': 'Integ', 'cost': 30, 'category': 'build'}  # 1,3,4,0
        techs['EnvEcon'] = {'name': 'Environmental Economics', 'prereq1': 'IndEcon', 'prereq2': 'EcoEng', 'cost': 30, 'category': 'build'}  # 0,0,4,3
        techs['Neural'] = {'name': 'Neural Grafting', 'prereq1': 'Brain', 'prereq2': 'IndAuto', 'cost': 35, 'category': 'conquer'}  # 3,1,1,1
        techs['BioEng'] = {'name': 'Bio-Engineering', 'prereq1': 'Gene', 'prereq2': 'Neural', 'cost': 35, 'category': 'build'}  # 0,2,3,2
        techs['CentEmp'] = {'name': 'Centauri Empathy', 'prereq1': 'Brain', 'prereq2': 'Ecology', 'cost': 35, 'category': 'explore'}  # 0,1,0,6
        techs['Alloys'] = {'name': 'Silksteel Alloys', 'prereq1': 'Subat', 'prereq2': 'IndAuto', 'cost': 35, 'category': 'build'}  # 3,0,4,2

        # Tier 4: Advanced technologies
        techs['DocSec'] = {'name': 'Photon/Wave Mechanics', 'prereq1': 'E=Mc2', 'prereq2': 'Alloys', 'cost': 40, 'category': 'conquer'}  # 3,2,2,0
        techs['Algor'] = {'name': 'Pre-Sentient Algorithms', 'prereq1': 'MilAlg', 'prereq2': 'Cyber', 'cost': 40, 'category': 'discover'}  # 2,4,3,2
        techs['Fusion'] = {'name': 'Fusion Power', 'prereq1': 'Algor', 'prereq2': 'Super', 'cost': 45, 'category': 'discover'}  # 3,4,3,1
        techs['E=Mc2'] = {'name': 'Applied Relativity', 'prereq1': 'Super', 'prereq2': 'Subat', 'cost': 40, 'category': 'discover'}  # 1,3,2,0
        techs['String'] = {'name': 'Superstring Theory', 'prereq1': 'Chaos', 'prereq2': 'Cyber', 'cost': 40, 'category': 'conquer'}  # 3,2,0,1
        techs['PlaEcon'] = {'name': 'Planetary Economics', 'prereq1': 'EnvEcon', 'prereq2': 'Integ', 'cost': 40, 'category': 'build'}  # 0,0,4,3
        techs['EcoEng2'] = {'name': 'Adv. Ecological Engineering', 'prereq1': 'Fusion', 'prereq2': 'EnvEcon', 'cost': 45, 'category': 'build'}  # 0,0,4,2
        techs['ProbMec'] = {'name': 'Probability Mechanics', 'prereq1': 'DocSec', 'prereq2': 'Algor', 'cost': 45, 'category': 'build'}  # 1,1,3,2
        techs['MindMac'] = {'name': 'Mind/Machine Interface', 'prereq1': 'DocAir', 'prereq2': 'Neural', 'cost': 45, 'category': 'conquer'}  # 4,0,2,2
        techs['Magnets'] = {'name': 'Monopole Magnets', 'prereq1': 'String', 'prereq2': 'Alloys', 'cost': 45, 'category': 'build'}  # 1,1,5,0
        techs['SupLube'] = {'name': 'Organic Superlubricant', 'prereq1': 'Fusion', 'prereq2': 'Fossil', 'cost': 45, 'category': 'conquer'}  # 3,1,2,0
        techs['NanoMin'] = {'name': 'Nanominiaturization', 'prereq1': 'Magnets', 'prereq2': 'SupLube', 'cost': 50, 'category': 'build'}  # 1,0,4,3
        techs['Unified'] = {'name': 'Unified Field Theory', 'prereq1': 'Magnets', 'prereq2': 'E=Mc2', 'cost': 50, 'category': 'conquer'}  # 4,3,0,1
        techs['Viral'] = {'name': 'Retroviral Engineering', 'prereq1': 'BioEng', 'prereq2': 'MilAlg', 'cost': 50, 'category': 'conquer'}  # 4,2,0,2
        techs['Orbital'] = {'name': 'Orbital Spaceflight', 'prereq1': 'DocAir', 'prereq2': 'Algor', 'cost': 50, 'category': 'discover'}  # 0,4,3,3
        techs['CentMed'] = {'name': 'Centauri Meditation', 'prereq1': 'EcoEng', 'prereq2': 'CentEmp', 'cost': 50, 'category': 'explore'}  # 0,0,2,4

        # Tier 5: Late-game technologies
        techs['Metal'] = {'name': 'Nanometallurgy', 'prereq1': 'ProbMec', 'prereq2': 'DocInit', 'cost': 55, 'category': 'explore'}  # 1,1,0,3
        techs['Surface'] = {'name': 'Frictionless Surfaces', 'prereq1': 'Unified', 'prereq2': 'IndRob', 'cost': 55, 'category': 'discover'}  # 1,3,2,0
        techs['MatComp'] = {'name': 'Matter Compression', 'prereq1': 'Metal', 'prereq2': 'NanoMin', 'cost': 55, 'category': 'conquer'}  # 3,1,2,0
        techs['Gravity'] = {'name': 'Graviton Theory', 'prereq1': 'QuanMac', 'prereq2': 'MindMac', 'cost': 55, 'category': 'explore'}  # 3,1,0,3
        techs['AGrav'] = {'name': 'Applied Gravitonics', 'prereq1': 'Gravity', 'prereq2': 'DigSent', 'cost': 60, 'category': 'explore'}  # 3,1,0,4
        techs['Quantum'] = {'name': 'Quantum Power', 'prereq1': 'Surface', 'prereq2': 'PlaEcon', 'cost': 55, 'category': 'discover'}  # 3,4,3,0
        techs['IndRob'] = {'name': 'Industrial Nanorobotics', 'prereq1': 'NanoMin', 'prereq2': 'IndAuto', 'cost': 55, 'category': 'build'}  # 3,1,8,1
        techs['Space'] = {'name': 'Advanced Spaceflight', 'prereq1': 'Orbital', 'prereq2': 'SupLube', 'cost': 55, 'category': 'discover'}  # 2,4,2,3
        techs['HomoSup'] = {'name': 'Homo Superior', 'prereq1': 'BioMac', 'prereq2': 'DocInit', 'cost': 60, 'category': 'explore'}  # 3,2,1,4
        techs['QuanMac'] = {'name': 'Quantum Machinery', 'prereq1': 'Quantum', 'prereq2': 'Metal', 'cost': 60, 'category': 'build'}  # 3,1,4,0
        techs['DigSent'] = {'name': 'Digital Sentience', 'prereq1': 'IndRob', 'prereq2': 'MindMac', 'cost': 60, 'category': 'discover'}  # 0,4,3,2
        techs['HAL9000'] = {'name': 'Self-Aware Machines', 'prereq1': 'Space', 'prereq2': 'DigSent', 'cost': 65, 'category': 'discover'}  # 0,4,3,3
        techs['BioMac'] = {'name': 'Biomachinery', 'prereq1': 'MindMac', 'prereq2': 'Viral', 'cost': 60, 'category': 'build'}  # 3,1,4,1
        techs['Solids'] = {'name': 'Super Tensile Solids', 'prereq1': 'MatComp', 'prereq2': 'Space', 'cost': 60, 'category': 'build'}  # 1,0,5,2
        techs['CentGen'] = {'name': 'Centauri Genetics', 'prereq1': 'CentMed', 'prereq2': 'Viral', 'cost': 60, 'category': 'explore'}  # 0,2,0,5
        techs['SentEco'] = {'name': 'Sentient Econometrics', 'prereq1': 'PlaEcon', 'prereq2': 'DigSent', 'cost': 65, 'category': 'explore'}  # 1,1,3,4

        # Tier 6: End-game technologies
        techs['SingMec'] = {'name': 'Singularity Mechanics', 'prereq1': 'Create', 'prereq2': 'HAL9000', 'cost': 70, 'category': 'discover'}  # 1,4,3,0
        techs['ConSing'] = {'name': 'Controlled Singularity', 'prereq1': 'SingMec', 'prereq2': 'AGrav', 'cost': 75, 'category': 'conquer'}  # 4,1,2,0
        techs['TempMec'] = {'name': 'Temporal Mechanics', 'prereq1': 'Eudaim', 'prereq2': 'Matter', 'cost': 70, 'category': 'build'}  # 0,1,3,2
        techs['CentPsi'] = {'name': 'Centauri Psi', 'prereq1': 'CentGen', 'prereq2': 'EcoEng2', 'cost': 65, 'category': 'explore'}  # 0,1,1,6
        techs['AlphCen'] = {'name': 'Secrets of Alpha Centauri', 'prereq1': 'CentPsi', 'prereq2': 'SentEco', 'cost': 75, 'category': 'discover'}  # 0,4,0,2
        techs['NanEdit'] = {'name': 'Matter Editation', 'prereq1': 'HAL9000', 'prereq2': 'Solids', 'cost': 70, 'category': 'build'}  # 1,2,3,1
        techs['Matter'] = {'name': 'Matter Transmission', 'prereq1': 'NanEdit', 'prereq2': 'AlphCen', 'cost': 75, 'category': 'build'}  # 1,0,3,2
        techs['WillPow'] = {'name': 'The Will to Power', 'prereq1': 'HomoSup', 'prereq2': 'CentPsi', 'cost': 70, 'category': 'explore'}  # 0,3,1,4
        techs['Eudaim'] = {'name': 'Eudaimonia', 'prereq1': 'SentEco', 'prereq2': 'WillPow', 'cost': 70, 'category': 'explore'}  # 0,0,3,4
        techs['Create'] = {'name': 'Secrets of Creation', 'prereq1': 'Unified', 'prereq2': 'WillPow', 'cost': 75, 'category': 'discover'}  # 1,4,1,0
        techs['Thresh'] = {'name': 'Threshold of Transcendence', 'prereq1': 'Create', 'prereq2': 'TempMec', 'cost': 80, 'category': 'explore'}  # 0,1,3,4
        techs['TranT'] = {'name': 'Transcendent Thought', 'prereq1': 'Thresh', 'prereq2': 'ConSing', 'cost': 100, 'category': 'build'}  # 0,2,0,0 (tied, choose build for balance)

        return techs

    def is_available(self, tech_id):
        """Check if a technology can be researched.

        Args:
            tech_id (str): Technology ID (e.g., 'Biogen')

        Returns:
            bool: True if prerequisites are met and not yet discovered
        """
        if tech_id not in self.technologies:
            return False

        if tech_id in self.discovered_techs:
            return False

        tech = self.technologies[tech_id]

        # Check prerequisite 1
        if tech['prereq1'] is not None and tech['prereq1'] not in self.discovered_techs:
            return False

        # Check prerequisite 2
        if tech['prereq2'] is not None and tech['prereq2'] not in self.discovered_techs:
            return False

        return True

    def get_available_techs(self):
        """Get all technologies that can currently be researched.

        Returns:
            list: List of (tech_id, tech_data) tuples for available techs
        """
        available = []
        for tech_id, tech_data in self.technologies.items():
            if self.is_available(tech_id):
                available.append((tech_id, tech_data))

        # Sort by cost (cheapest first)
        available.sort(key=lambda x: x[1]['cost'])
        return available

    def set_current_research(self, tech_id):
        """Set the technology to research.

        Args:
            tech_id (str): Technology ID to research
        """
        if self.is_available(tech_id):
            self.current_research = tech_id
            self.research_accumulated = 0

    def get_current_tech(self):
        """Get the name of the technology currently being researched.

        Returns:
            str: Name of current tech, or None if no research active
        """
        if self.current_research is None:
            return None
        return self.technologies[self.current_research]['name']

    def get_research_cost(self):
        """Get the research cost of the current technology.

        Returns:
            int: Research points needed
        """
        if self.current_research is None:
            return 0

        base_cost = self.technologies[self.current_research]['cost']

        # Cost scales with number of techs discovered
        # Formula: base * (1 + num_discovered * 0.05)
        multiplier = 1.0 + (len(self.discovered_techs) * 0.05)

        return int(base_cost * multiplier)

    def get_turns_remaining(self):
        """Calculate turns remaining until current tech is complete.

        Returns:
            int: Estimated turns to completion, or 0 if no research
        """
        if self.current_research is None:
            return 0

        remaining = self.get_research_cost() - self.research_accumulated
        if self.research_per_turn <= 0:
            return 999

        return max(1, (remaining + self.research_per_turn - 1) // self.research_per_turn)

    def auto_select_research(self):
        """Automatically select a technology to research.

        Chooses randomly from available techs weighted by cost (cheaper preferred).
        """
        import random

        available = self.get_available_techs()
        if not available:
            return

        # Randomly select from available techs
        tech_id = random.choice([t[0] for t in available])
        self.set_current_research(tech_id)

    def process_turn(self):
        """Process research for one turn.

        Adds research points and checks for tech completion.
        Auto-selects next research if none active.

        Returns:
            str or None: Tech ID of completed tech, or None if no completion
        """
        # Auto-select research if none active
        if self.current_research is None:
            self.auto_select_research()
            if self.current_research is None:
                return None

        self.research_accumulated += self.research_per_turn

        # Check for tech completion
        if self.research_accumulated >= self.get_research_cost():
            completed_tech = self.current_research
            self.discovered_techs.add(completed_tech)
            tech_name = self.technologies[completed_tech]['name']
            print(f"Technology discovered: {tech_name}!")

            # Reset research and auto-select next
            self.current_research = None
            self.research_accumulated = 0
            self.auto_select_research()

            return completed_tech

        return None

    def get_progress_percentage(self):
        """Get research progress as a percentage.

        Returns:
            float: Progress from 0.0 to 1.0
        """
        if self.current_research is None:
            return 0.0

        cost = self.get_research_cost()
        if cost <= 0:
            return 1.0

        return min(1.0, self.research_accumulated / cost)

    def get_tech_status(self, tech_id):
        """Get the status of a specific technology.

        Args:
            tech_id (str): Technology ID

        Returns:
            str: "Completed", "Researching", "Available", or "Locked"
        """
        if tech_id in self.discovered_techs:
            return "Completed"
        elif tech_id == self.current_research:
            return "Researching"
        elif self.is_available(tech_id):
            return "Available"
        else:
            return "Locked"

    def get_current_category(self):
        """Get the category of the technology currently being researched.

        Returns:
            str: Category ('explore', 'discover', 'build', 'conquer') or None
        """
        if self.current_research is None:
            return None
        return self.technologies[self.current_research].get('category', None)

    def get_category_color(self, category):
        """Get the RGB color for a tech category.

        Args:
            category (str): 'explore', 'discover', 'build', or 'conquer'

        Returns:
            tuple: RGB color (R, G, B)
        """
        colors = {
            'explore': (50, 200, 50),    # Green
            'discover': (150, 150, 150),  # Gray
            'build': (220, 180, 50),      # Yellow
            'conquer': (220, 50, 50)      # Red
        }
        return colors.get(category, (255, 255, 255))  # Default white

    def has_tech(self, tech_id):
        """Check if a technology has been discovered.

        Args:
            tech_id (str): Technology ID

        Returns:
            bool: True if discovered
        """
        return tech_id in self.discovered_techs
