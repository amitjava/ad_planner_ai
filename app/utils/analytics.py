"""Analytics utilities for reach and budget calculations"""
import re
import math
from typing import Dict


def calculate_reach_percentage(reach_string: str, location: str, is_local: bool) -> Dict:
    """
    Calculate what percentage of target population is reached

    Args:
        reach_string: String like "15,000-20,000 people"
        location: Business location (city, state, or ZIP code)
        is_local: Whether this is a local or national campaign

    Returns:
        Dictionary with reach analytics including percentages
    """
    # Extract reach numbers from string
    numbers = re.findall(r'[\d,]+', reach_string)

    if not numbers:
        return {
            "reach_min": 0,
            "reach_max": 0,
            "percentage": "Unknown",
            "population_estimate": "Unknown"
        }

    # Parse the numbers
    reach_min = int(numbers[0].replace(',', ''))
    reach_max = int(numbers[1].replace(',', '')) if len(numbers) > 1 else reach_min

    # Estimate target population based on location
    # These are rough estimates - in production use real demographic data
    population_estimates = {
        # Major US cities (adults 18-65 in metro area)
        "new york": 8_000_000,
        "los angeles": 5_000_000,
        "chicago": 3_500_000,
        "san francisco": 1_200_000,
        "seattle": 900_000,
        "boston": 800_000,
        "portland": 700_000,
        "denver": 800_000,
        "austin": 1_000_000,
        "miami": 900_000,
    }

    # Try to match location
    location_lower = location.lower()
    population = None

    for city, pop in population_estimates.items():
        if city in location_lower:
            population = pop
            break

    # Default estimates
    if population is None:
        if is_local:
            population = 500_000  # Small to medium city
        else:
            population = 10_000_000  # National campaign

    # If local business, assume target is 20-30% of total population
    if is_local:
        target_population = int(population * 0.25)
    else:
        target_population = population

    # Calculate percentage
    percentage_min = (reach_min / target_population) * 100
    percentage_max = (reach_max / target_population) * 100

    return {
        "reach_min": reach_min,
        "reach_max": reach_max,
        "target_population": target_population,
        "percentage_min": round(percentage_min, 1),
        "percentage_max": round(percentage_max, 1),
        "percentage_display": f"{round(percentage_min, 1)}%-{round(percentage_max, 1)}%"
    }


def calculate_budget_scaling(
    current_budget: int,
    current_reach_min: int,
    current_reach_max: int,
    target_multiplier: float = 2.0
) -> Dict:
    """
    Calculate budget needed to scale reach by a given multiplier

    Uses diminishing returns model - doubling reach typically requires
    more than doubling budget due to audience saturation, higher CPMs,
    and ad fatigue.

    Args:
        current_budget: Current monthly budget in dollars
        current_reach_min: Current minimum reach
        current_reach_max: Current maximum reach
        target_multiplier: How much to multiply reach by (default 2.0 for doubling)

    Returns:
        Dictionary with budget recommendations and reach projections
    """
    # Calculate average current reach
    current_reach_avg = (current_reach_min + current_reach_max) / 2

    # Target reach
    target_reach_min = int(current_reach_min * target_multiplier)
    target_reach_max = int(current_reach_max * target_multiplier)
    target_reach_avg = int(current_reach_avg * target_multiplier)

    # Budget scaling with diminishing returns
    # Using logarithmic scale: budget_multiplier = multiplier^1.3
    # This accounts for:
    # - Audience saturation
    # - Higher CPMs for broader targeting
    # - Ad fatigue
    budget_multiplier = math.pow(target_multiplier, 1.3)
    recommended_budget = int(current_budget * budget_multiplier)

    # Calculate cost per person reached
    current_cost_per_reach = current_budget / current_reach_avg if current_reach_avg > 0 else 0
    new_cost_per_reach = recommended_budget / target_reach_avg if target_reach_avg > 0 else 0

    return {
        "current_budget": current_budget,
        "recommended_budget": recommended_budget,
        "budget_increase": recommended_budget - current_budget,
        "budget_increase_percent": round(
            ((recommended_budget / current_budget) - 1) * 100, 1
        ) if current_budget > 0 else 0,
        "current_reach_range": f"{current_reach_min:,}-{current_reach_max:,}",
        "target_reach_range": f"{target_reach_min:,}-{target_reach_max:,}",
        "current_cost_per_reach": round(current_cost_per_reach, 2),
        "new_cost_per_reach": round(new_cost_per_reach, 2),
        "efficiency_change_percent": round(
            ((new_cost_per_reach / current_cost_per_reach) - 1) * 100, 1
        ) if current_cost_per_reach > 0 else 0
    }
