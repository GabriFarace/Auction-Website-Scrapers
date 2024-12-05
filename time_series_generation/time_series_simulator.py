import numpy as np
import matplotlib.pyplot as plt
import json


# Parse the configuration JSON
with open("config_series.json", "r") as f:
    config = json.load(f)


def generate_trend(length, initial_value=0, slope=0):
    """Generates a linear trend with a given initial value and slope."""
    return initial_value + slope * np.arange(length)


def generate_seasonality(length, period, amplitude):
    """Generates a sinusoidal seasonality component."""
    return amplitude * np.sin(2 * np.pi * np.arange(length) / period)


def generate_noise(length, std_dev):
    """Generates random noise."""
    return np.random.normal(0, std_dev, length)


def introduce_trend_changes(trend, change_points, slopes):
    """Introduces changes in trend at specified change points."""
    change_points = np.sort(change_points)
    change_points_list = [c for c in change_points] + [len(trend)]
    for i in range (len(change_points_list) - 1):
        trend[change_points_list[i]:change_points_list[i+1]] += slopes[i] * np.arange(change_points_list[i+1] - change_points_list[i])
    return trend


def add_spikes(series, num_spikes, spike_magnitude):
    """Adds random spikes to the series."""
    spike_indices = np.random.choice(len(series), num_spikes, replace=False)
    for idx in spike_indices:
        series[idx] += np.random.uniform(-spike_magnitude, spike_magnitude)
    return series


def scale_time_series_to_sum(time_series, target_sum_mean, target_sum_std):
    """Scale the time series so that its sum lies within the desired mean ± std deviation range."""
    actual_sum = np.sum(time_series)

    # Desired sum: sample from normal distribution around the target mean
    desired_sum = np.random.normal(target_sum_mean, target_sum_std)

    # Compute the scaling factor to match the desired sum
    scaling_factor = desired_sum / actual_sum

    # Scale the time series
    scaled_time_series = time_series * scaling_factor

    # Ensure no negative values after scaling
    scaled_time_series = np.clip(scaled_time_series, 0, None)

    return scaled_time_series


def generate_random_parameters():
    """Generate random parameters for the time series generation based on the config."""
    sum_mean = np.random.uniform(config['sum_mean']['min'], config['sum_mean']['max'])
    sum_std = np.random.uniform(0, sum_mean/2)

    # Sample random values from the specified ranges in the config
    length = np.random.randint(config['length']['min'], config['length']['max'] + 1)
    magnitude_unit = (sum_mean/length)
    std_unit = (sum_std/length)
    initial_value = np.random.uniform(magnitude_unit - std_unit, magnitude_unit + std_unit)
    base_slope = np.random.uniform(config['base_slope']['min'], config['base_slope']['max'])
    seasonal_amplitude = np.random.uniform(magnitude_unit - std_unit, magnitude_unit + std_unit)
    seasonal_period = np.random.randint(config['seasonal_period']['min'], config['seasonal_period']['max'] + 1)
    noise_std = np.random.uniform(0, std_unit/100)

    num_change_points = np.random.randint(config['num_change_points']['min'], config['num_change_points']['max'] + 1)
    change_points = np.random.choice(range(1, length), num_change_points, replace=False)
    slopes = np.random.uniform(-magnitude_unit*0.001, magnitude_unit*0.001, num_change_points)

    num_spikes = np.random.randint(config['num_spikes']['min'], config['num_spikes']['max'] + 1)
    spike_magnitude = np.random.uniform(magnitude_unit - std_unit, magnitude_unit + std_unit)

    # Randomly decide whether to include seasonality (True or False)
    include_seasonality = np.random.choice([True, False])

    return {
        'length': length,
        'initial_value': initial_value,
        'base_slope': base_slope,
        'seasonal_amplitude': seasonal_amplitude,
        'seasonal_period': seasonal_period,
        'noise_std': noise_std,
        'change_points': change_points,
        'slopes': slopes,
        'num_spikes': num_spikes,
        'spike_magnitude': spike_magnitude,
        'include_seasonality': include_seasonality,
        'sum_mean': sum_mean,
        'sum_std': sum_std
    }


def generate_time_series_with_random_params():
    """Generates a time series with random parameters based on the config."""
    params = generate_random_parameters()

    # Generate base trend
    trend = generate_trend(params['length'], params['initial_value'], params['base_slope'])

    # Introduce trend changes
    trend = introduce_trend_changes(trend, params['change_points'], params['slopes'])

    # Add seasonality only if the flag is True
    if params['include_seasonality']:
        seasonality = generate_seasonality(params['length'], params['seasonal_period'], params['seasonal_amplitude'])
    else:
        seasonality = np.zeros(params['length'])  # No seasonality, just zeros

    # Add noise
    noise = generate_noise(params['length'], params['noise_std'])

    # Combine components
    time_series = trend + seasonality + noise

    # Add spikes
    time_series = add_spikes(time_series, params['num_spikes'], params['spike_magnitude'])

    # Scale the time series to match the target sum mean and std
    time_series = scale_time_series_to_sum(time_series, params['sum_mean'], params['sum_std'])

    # Ensure values do not drop below zero
    time_series = np.clip(time_series, 0, None)  # Clipping all negative values to 0

    return time_series, params


done = False
while not done:
    # Example usage: Generate a time series with random parameters and plot it
    time_series, params = generate_time_series_with_random_params()

    # Plot the result
    plt.figure(figsize=(12, 6))
    plt.plot(time_series, label="Generated Time Series")
    plt.title(f"Generated Time Series (Sum Mean: {params['sum_mean']:.2f}, Sum Std: {params['sum_std']:.2f})")
    plt.xlabel("Time (Days)")
    plt.ylabel("Value")
    plt.legend()
    plt.show()

    # Print parameters used for the generation
    print("Parameters used to generate the time series:")
    print(params)

    choice = input("Would you like to generate another time series? (y/n): ").lower()
    if choice == 'n':
        done = True
