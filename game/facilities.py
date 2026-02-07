# facilities.py
"""Base facility definitions from Alpha Centauri alpha.txt.

This module contains all base facilities (buildings) and secret projects
that can be constructed in bases. Each facility has tech prerequisites,
costs, maintenance, and effects.
"""
from game.data.facility_data import FACILITIES, SECRET_PROJECTS


def get_facility_by_id(facility_id):
    """Get facility data by ID.

    Args:
        facility_id (str): Facility ID

    Returns:
        dict: Facility data, or None if not found
    """
    for facility in FACILITIES:
        if facility['id'] == facility_id:
            return facility
    for project in SECRET_PROJECTS:
        if project['id'] == facility_id:
            return project
    return None


def get_facility_by_name(name):
    """Get facility data by name.

    Args:
        name (str): Facility name

    Returns:
        dict: Facility data, or None if not found
    """
    for facility in FACILITIES:
        if facility['name'] == name:
            return facility
    for project in SECRET_PROJECTS:
        if project['name'] == name:
            return project
    return None


def is_facility_available(facility, tech_tree):
    """Check if a facility can be built based on tech prerequisites.

    Args:
        facility (dict): Facility data with 'prereq' field
        tech_tree (TechTree): Player's tech tree

    Returns:
        bool: True if facility is unlocked
    """
    if facility['prereq'] is None:
        return True
    return tech_tree.has_tech(facility['prereq'])


def get_available_facilities(tech_tree):
    """Get all facilities available to build based on current techs.

    Args:
        tech_tree (TechTree): Player's tech tree

    Returns:
        list: List of available facility dicts
    """
    available = []
    for facility in FACILITIES:
        if is_facility_available(facility, tech_tree):
            available.append(facility)
    return available


def get_available_projects(tech_tree, built_projects):
    """Get all secret projects available to build.

    Args:
        tech_tree (TechTree): Player's tech tree
        built_projects (set): Set of project IDs already built globally

    Returns:
        list: List of available project dicts
    """
    available = []
    for project in SECRET_PROJECTS:
        if project['id'] not in built_projects and is_facility_available(project, tech_tree):
            available.append(project)
    return available
