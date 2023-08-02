import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class StrawHouseAnalysis:
    def __init__(self, file_path, country, H=25, R=10, starting_year=1950, degradation_rate=0.02, growth_rate=0.05):
        self.data = self.__read_data(file_path)
        self.country = country
        self.R = R
        self.H = H
        self.starting_year = starting_year
        self.degradation_rate = degradation_rate
        self.growth_rate = growth_rate

    def __read_data(self, file_path):
        # Reads the CSV file
        # df = pd.read_csv('https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv')
        return pd.read_csv(file_path)

    def __filter_and_calculate(self):
        # Filters data for the given country and calculates the adjusted carbon footprint
        country_data = self.data[self.data['country'] == self.country].copy()
        country_data['C_housing'] = country_data['co2'] * (self.H / 100)
        
        # Assumes exponential growth in the number of straw houses starting from the given year
        country_data['S'] = (country_data['year'] >= self.starting_year) * np.exp(self.growth_rate * (country_data['year'] - self.starting_year))
        
        # Applies degradation function
        degradation_factor = 1 - self.degradation_rate
        country_data['S'] *= degradation_factor ** (country_data['year'] - self.starting_year)
        
        country_data['C_straw'] = country_data['S'] * self.R
        country_data['C_adjusted'] = country_data['C_housing'] - country_data['C_straw']
        return country_data[['year', 'C_housing', 'C_straw', 'C_adjusted']]

    def __plot_results(self, data):
        # Plots the results
        plt.figure(figsize=[14, 7])
        plt.plot(data['year'], data['C_housing'], label='Original Carbon Footprint (C_housing)')
        plt.plot(data['year'], data['C_straw'], label='Reduction Due to Straw Houses (C_straw)')
        plt.plot(data['year'], data['C_adjusted'], label='Adjusted Carbon Footprint (C_adjusted)', linestyle='--')
        plt.title('Impact of Straw Houses on Carbon Footprint of Housing Industry')
        plt.xlabel('Year')
        plt.ylabel('Carbon Footprint (Metric Tons CO2)')
        plt.legend()
        plt.grid(True)
        plt.show()

    def analyze(self):
        # Orchestrates the analysis and calls the private methods
        analysis_data = self.__filter_and_calculate()
        self.__plot_results(analysis_data)

if __name__ == "__main__":
    df_url = 'https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv'
    analysis = StrawHouseAnalysis(df_url, 'Germany')
    analysis.analyze()

