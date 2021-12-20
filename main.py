# ImageTk and Image allow us to use custom images in tkinter windows
from typing import Dict, List
from tkinter import *
import sys
import os
from PIL import ImageTk, Image
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

cwd = Path.cwd()

weeks_in_a_year = 52
grams_in_a_kilo = 1000
kg_per_year_to_g_per_week = grams_in_a_kilo / weeks_in_a_year

animal_types = ['Beef', 'Poultry', 'Pork', 'Lamb']

emissions_per_animal = {'Beef': 498.9,
                        'Poultry': 57.0,
                        'Pork': 76.1,
                        'Lamb': 198.5,
                        }
# grams of CO2 emissions per gram of protein

serving_size_per_animal = {'Beef': 85,
                           'Poultry': 85,
                           'Pork': 100,
                           'Lamb': 100,
                           }
# average meal is 3 to 3.5 ounces,
# which equates to these values in grams per meat

emissions_per_serving_of_animal = {x: emissions_per_animal[x] * serving_size_per_animal[x]
                                   for x in emissions_per_animal}


class Country:
    """
    The country the user is located in.

    Attributes:
        - name: name of the country
        - average_consumption: the average meat consumption per year per person
        by meat type in this country

    Representation Invariants:
        - name in proper_country_data

    Sample Usage:
    >>> Canada = Country('Canada', {'Beef' :18, 'Pork':24, 'Lamb': 1, 'Poultry': 39})
    """
    name: str
    average_consumption: Dict[str, int]

    def __init__(self, name, average_consumption) -> None:
        self.name = name
        self.average_consumption = average_consumption
    # The following is generic class init, as seen in lecture


country_data = pd.read_csv(
    f'{cwd}/assets/percapita.csv')
proper_country_data = {
    country_data.loc[x, 'Entity']: [country_data.loc
                                    [x, 'Bovine meat food supply quantity '
                                        '(kg/capita/yr) (FAO, 2020)'],
                                    country_data.loc
                                    [x, 'Poultry meat food supply quantity '
                                        '(kg/capita/yr) (FAO, 2020)'],
                                    country_data.loc
                                    [x, 'Pigmeat food supply quantity '
                                        '(kg/capita/yr) (FAO, 2020)'],
                                    country_data.loc
                                    [x, 'Mutton & Goat meat food supply quantity '
                                        '(kg/capita/yr) (FAO, 2020)']]
    for x in range(2, 11025) if country_data.loc
                                [x, 'Year'] > country_data.loc[x + 1, 'Year']}

countries = {}
for country in proper_country_data:
    countries[country] = Country(country, {'Beef': proper_country_data[country][0] *
                                                   kg_per_year_to_g_per_week,
                                           'Pork': proper_country_data[country][2] *
                                                   kg_per_year_to_g_per_week,
                                           'Lamb': proper_country_data[country][3] *
                                                   kg_per_year_to_g_per_week,
                                           'Poultry': proper_country_data[country][1] *
                                                      kg_per_year_to_g_per_week})


# countries is in grams of animal eaten per week, once adjusted


class Animal:
    """
    A type of meat the user eats weekly.

    Attributes:
        - name: the name of the type of meat
        - location: the country the user resides in
        - weekly_consumption: servings of this meat user consumes per week
        - country_emissions: Average C02 emissions produced from consumption of
        this animal in this country in grams per week
        - consumption_difference: the difference between the user's meat consumption and the
        average person's meat consumption in the user's country in this particular meat type
        - consumption_comparison: the percentage difference between the user's meat
        consumption and the average person's meat consumption in the user's country in
        this particular meat type
        - weekly_emissions: the user's weekly emissions from consuming this particular meat type
        - new_consumption: the consumer's new weekly consumption of this meat type
        - new_emissions: the CO2 emissions of the consumer's new weekly consumption of this
        meat type
        - emission_reduction: the amount of CO2 emissions reduced between the original and new
        consumer's weekly consumption of this meat type
        - emission_reduction_percentage: the percentage of CO2 emissions reduced between the
        orginal and new consumer's weekly consumption of this meat type

    Sample Usage:
    >>> Beef = Animal('Beef', 'Canada', 15.0)
    >>> Beef.find_stats
    >>> Beef.weekly_emissions
    7483.5
    >>> Beef.consumption_difference
    3.0
    """
    name: str
    location: Country
    weekly_consumption: float
    country_emissions: float

    consumption_difference: float
    consumption_comparison: float
    weekly_emissions: float

    new_consumption: float
    new_emissions: float
    emission_reduction: float
    emission_reduction_percentage: float

    def __init__(self, name, location, weekly_consumption) -> None:
        """
        Initialize a new meat type that the user consumes with a given name, the user's country,
        and its yearly consumption of that meat.

        Preconditions:
            - name in emissions_per_animal
        """
        self.name = name
        self.location = location
        self.weekly_consumption = weekly_consumption
        self.country_emissions = emissions_per_animal[self.name] * \
                                 self.location.average_consumption[self.name]

    def find_stats(self) -> None:
        """
        Computes the weekly_emissions, consumption_difference, and consumption_comparison
        of the given Animal Object.
        """
        self.weekly_emissions = self.weekly_consumption * \
                                emissions_per_serving_of_animal[self.name]
        self.consumption_difference = self.weekly_consumption - \
                                      self.location.average_consumption[self.name]
        self.consumption_comparison = 100 * self.consumption_difference / \
                                      self.location.average_consumption[self.name]

    def consumption_goals(self, new_consumption) -> None:
        """
        Computes the new_emissions, emission_reduction, and emission_reduction_percentage
        of the given Animal Object.
        """
        self.new_consumption = new_consumption
        self.new_emissions = new_consumption * emissions_per_serving_of_animal[self.name]
        self.emission_reduction = self.weekly_emissions - self.new_emissions
        if self.weekly_emissions != 0:
            self.emission_reduction_percentage = 100 * self.emission_reduction / \
                                                 self.weekly_emissions
        else:
            self.emission_reduction_percentage = 0


class User:
    """
    A consumer of Meat Monitor.

    Attributes:
        - name: name of the user
        - location: the country the user is located in
        - animal_list: the type of meats that the user eats on a weekly basis
        - total_emissions: the total CO2 emissions emitted to produce the user's meat consumption
        - total_country_emissions: the total CO2 emissions emitted to produce the average
        person's meat consumption in the user's country
        - total_emissions_comparison: the difference between the user's CO2 emissions from
        meat consumption and the average person's CO2 emissions from meat consumption in the
        user's country
        - total_emissions_percentage: the percentage difference between the user's CO2 emissions
        from meat consumption and the average person's CO2 emissions from meat consumption in
        the user's country
        - new_total_emissions: the total CO2 emissions in the user's goal meat consumption
        - emission_reduction: the CO2 emissions reduced in the user's goal meat consumption
        compared to his or her original meat consumption.
        - emission_reduction_percentage: the percentage of total CO2 emissions reduced in the
        user's goal meat consumption compared to his or her original meat consumption.

    Sample Usage:
    >>> Jeremy = User('Jeremy', 'Canada')
    >>> Jeremy.create_animal_classes([2, 3, 5, 7])
    >>> Jeremy.find_stats()
    >>> Jeremy.total_emissions
    240808.0

    """
    name: str
    location: Country
    animal_list: Dict[str, Animal]
    total_emissions: float
    total_country_emissions: float
    total_emissions_comparison: float
    total_emissions_percentage: float
    total_emissions_list: List[float]
    total_country_emissions_list: List[float]

    new_total_emissions: float
    new_total_emissions_list: List[float]
    emission_reduction: float
    emission_reduction_percentage: float

    def __init__(self, name, location) -> None:
        """
        Initialize a new user with a given name and country.

        Preconditions:
            - location in countries
        """
        self.name = name
        self.location = countries[location]
        self.animal_list = {}

    def create_animal_classes(self, servings: [float]) -> None:
        """
        Fills animal_list with meat consumption values for each animal key.
        """
        for x in range(0, len(animal_types)):
            self.animal_list[animal_types[x]] = Animal(animal_types[x], self.location, servings[x])

    def create_goals(self, servings: [float]) -> None:
        """
        Creates second list with new meat consumption goals for each animal.
        """
        for x in range(0, len(self.animal_list)):
            self.animal_list[animal_types[x]].consumption_goals(servings[x])

    def find_stats(self) -> None:
        """
        Computes total_emissions, total_country_emissions, total_emissions_comparison,
        and total_emissions_percentage.
        """
        for animal in self.animal_list:
            self.animal_list[animal].find_stats()

        self.total_emissions = sum([self.animal_list[animal].weekly_emissions \
                                    for animal in self.animal_list])
        self.total_country_emissions = sum([self.animal_list[animal].country_emissions \
                                            for animal in self.animal_list])

        self.total_emissions_comparison = self.total_emissions - \
                                          self.total_country_emissions
        self.total_emissions_percentage = 100 * self.total_emissions_comparison / \
                                          self.total_country_emissions

    def goal_stats(self) -> None:
        """
        Computes new_total_emissions, emission_reduction, and emission_reduction_percentage.
        """
        self.new_total_emissions = sum([self.animal_list[animal].new_emissions \
                                        for animal in self.animal_list])
        self.emission_reduction = self.total_emissions - self.new_total_emissions
        if self.total_emissions != 0:
            self.emission_reduction_percentage = 100 * self.emission_reduction / \
                                                 self.total_emissions
        else:
            self.emission_reduction_percentage = 0


# This is the function that is triggered after the loading screen/slash page expires
# It creates a new window where the user inputs their information


def inputs() -> None:
    """ Creates and initializes the page where user inputs their information.
    Preconditions:
                - len(e_name.get()) < 11
                - (e_name.get()) != ''
                - (e_country.get()) != ''
    """
    global root
    splash_root.destroy()
    # Creates a new global window whose information can subsequently be accessed by other windows
    # Destroys the opening page window

    root = Tk()
    root.title('Meat Monitor')
    root_x = int((root.winfo_screenwidth() / 2) - (800 / 2))
    root_y = int((root.winfo_screenheight() / 2) - (600 / 2))
    root.geometry(f'{800}x{600}+{root_x}+{root_y}')
    root.configure(background='lavender')
    # Sets up a new window that exists at the center of the user's screen regardless of resolution

    frame = Frame(master=root, width=750, height=550, background='lavender')
    frame.pack()
    # Creates a frame in which we can add elements like buttons and input boxes

    global graphic
    png2 = Image.open(
        f'{cwd}/assets/splash3.png')
    resized_png2 = png2.resize((300, 150), Image.ANTIALIAS)
    graphic = ImageTk.PhotoImage(resized_png2)
    graphic_label1 = Label(frame, image=graphic, background='lavender')
    # Added logo to top of the frame by importing,
    # resizing it and assigning it to a label to be shown

    e_beef = Scale(frame, from_=0, to=15, orient=HORIZONTAL,
                   background='lavender', fg='purple', length=150)
    e_poultry = Scale(frame, from_=0, to=15, orient=HORIZONTAL,
                      background='lavender', fg='purple', length=150)
    e_pork = Scale(frame, from_=0, to=15, orient=HORIZONTAL,
                   background='lavender', fg='purple', length=150)
    e_lamb = Scale(frame, from_=0, to=15, orient=HORIZONTAL,
                   background='lavender', fg='purple', length=150)
    e_name = Entry(frame, width=15, fg='purple')
    # e_country = Entry(frame, width=15, fg='purple')
    options = [x for x in countries]

    e_country = StringVar()
    e_country.set('Country')

    drop = OptionMenu(frame, e_country, *options)
    # Created 5 sliders for users to input their information and 2 input boxes

    question = Label(frame,
                     text="How many servings of each type of meat would you say you have per week?",
                     fg='purple', background='lavender', font=('Helvetica', 18))
    question2 = Label(frame, text="Input the following information to "
                                  "calculate your diet's carbon footprint:",
                      fg='purple', background='lavender', font=('Helvetica', 18))
    q_beef = Label(frame, text='Beef: ', fg='purple', background='lavender', font=('Helvetica', 15))
    q_poultry = Label(frame, text='Chicken: ', fg='purple',
                      background='lavender', font=('Helvetica', 15))
    q_pork = Label(frame, text='Pork: ', fg='purple', background='lavender', font=('Helvetica', 15))
    q_lamb = Label(frame, text='Lamb: ', fg='purple', background='lavender', font=('Helvetica', 15))
    q_name = Label(frame, text='Name: ', fg='purple', background='lavender', font=('Helvetica', 15))
    q_country = Label(frame, text='Country: ', fg='purple',
                      background='lavender', font=('Helvetica', 15))

    # Created 7 text labels explaining to the user what information to provide

    # Nested function that allows a button to pull and store user inputted data
    # Also creates a new page with all the results

    def write() -> None:
        """ Gets values from input boxes to be later manipulated by backend functions. """

        global user1
        user1 = User(e_name.get(), e_country.get())
        user1.create_animal_classes([float(e_beef.get()), float(e_poultry.get()),
                                     float(e_pork.get()), float(e_lamb.get())])
        user1.find_stats()
        # Built in functions to get the user's data

        # *output is the user's final carbon footprint basically
        output = int(user1.total_emissions / 1000)

        root.destroy()

        # Destroys the input

        def graph() -> None:
            """Creates graphs of info using matplotlib
            Preconditions:
                - user1.total_emissions_list != []
                - user1.total_country_emissions_list != []
                - user1.new_total_emissions_list != []
                - Adjust button in front end must be pressed
            """
            if user1.total_emissions_percentage <= -25:
                user1.total_emissions_list = [user1.animal_list[animal].weekly_emissions / 1000
                                              for animal in user1.animal_list]
                user1.total_country_emissions_list = [user1.animal_list[animal].country_emissions
                                                      / 1000 for animal in user1.animal_list]
                w = 0.2

                bar1 = np.arange(len(animal_types))
                bar2 = [x + w for x in bar1]

                plt.bar(bar1, user1.total_emissions_list, w, label='Your Current Emissions')
                plt.bar(bar2, user1.total_country_emissions_list, w,
                        label='Average Emissions per Capita for Your Country')

                plt.xlabel('Types of Meat')
                plt.ylabel('Kg of CO2 Emissions per Week')
                plt.title('Weekly Kg of CO2 Emissions from Eating Meat')
                plt.xticks(bar1 + w / 2, animal_types)
                plt.legend()
                plt.show()
            else:
                user1.total_emissions_list = [user1.animal_list[animal].weekly_emissions / 1000
                                              for animal in user1.animal_list]
                user1.total_country_emissions_list = [user1.animal_list[animal].country_emissions
                                                      / 1000 for animal in user1.animal_list]
                user1.new_total_emissions_list = [user1.animal_list[animal].new_emissions
                                                  / 1000 for animal in user1.animal_list]

                w = 0.2

                bar1 = np.arange(len(animal_types))
                bar2 = [x + w for x in bar1]
                bar3 = [x + w for x in bar2]

                plt.bar(bar1, user1.total_emissions_list, w, label='Your Current Emissions')
                plt.bar(bar2, user1.new_total_emissions_list, w, label='Your Updated Emissions')
                plt.bar(bar3, user1.total_country_emissions_list, w,
                        label='Average Emissions per Capita for Your Country')

                plt.xlabel('Types of Meat')
                plt.ylabel('Kg of CO2 Emissions per Week')
                plt.title('Weekly Kg of CO2 Emissions from Eating Meat')
                plt.xticks(bar1 + w, animal_types)
                plt.legend()
                plt.show()

        root1 = Tk()
        root1.title('Meat Monitor')
        root1_x = int((root1.winfo_screenwidth() / 2) - (800 / 2))
        root1_y = int((root1.winfo_screenheight() / 2) - (600 / 2))
        root1.geometry(f'{800}x{600}+{root1_x}+{root1_y}')
        root1.configure(background='lavender')
        # Sets up a new window identical to the previous one

        frame1 = Frame(master=root1, width=750, height=600, background='lavender')
        frame1.pack()
        # Sets up a new frame similar to the previous one

        global graphic2
        png3 = Image.open(
            f'{cwd}/assets/splash3.png')
        resized_png3 = png3.resize((300, 150), Image.ANTIALIAS)
        graphic2 = ImageTk.PhotoImage(resized_png3)
        graphic_label2 = Label(frame1, image=graphic2, background='lavender')
        graphic_label2.place(x=225, y=0)

        # Sets up the same graphic on previous window

        def restart() -> None:
            """Ends the program and takes the user back to the splash page. """
            python = sys.executable
            os.execl(python, python, *sys.argv)

            # If the user's carbon footprint is less than X value,
            # show a screen that says they do not need to make changes

        # Else, show them a screen where they are allowed to calculate
        # a new diet to reduce their carbon footprint
        if user1.total_emissions_percentage <= -25:
            text = Label(frame1,
                         text=f'Congratulations {user1.name}! Your total CO2 emissions are more ',
                         fg='purple', background='lavender', font=('Helvetica', 25))
            text3 = Label(frame1, text=f'than 25% less than the average'
                                       f' person from {user1.location.name}, at just:',
                          fg='purple', background='lavender', font=('Helvetica', 25))
            result = Label(frame1, text=output, fg='green',
                           background='lavender', font=('Helvetica', 60))
            graph = Button(frame1, text='View Graphical Analysis', padx=30, pady=10, command=graph,
                           background='lavender', font=('Helvetica', 15))
            text2 = Label(frame1, text='You do not need to make any changes to your diet!',
                          fg='purple', background='lavender', font=('Helvetica', 25))

            restart = Button(frame1, text='Restart', padx=30, pady=10, command=restart,
                             fg='purple', background='lavender', font=('Helvetica', 15))
            restart.place(x=600, y=550)
            text.place(x=50, y=125)
            text3.place(x=30, y=160)
            result.place(x=325, y=200)
            text2.place(x=100, y=300)
            graph.place(x=260, y=400)
            # Sets up various labels and organizes them in the frame
        else:
            text = Label(frame1, text=f'{user1.name}, your total CO2 (kg/week) emissions are:',
                         fg='purple', background='lavender', font=('Helvetica', 25))

            if user1.total_emissions_percentage <= 25:
                result = Label(frame1, text=f'{output} →', fg='yellow',
                               background='lavender', font=('Helvetica', 60))
            else:
                result = Label(frame1, text=f'{output} →', fg='red',
                               background='lavender', font=('Helvetica', 60))

            beef_slider = Scale(frame1, from_=0, to=15, orient=HORIZONTAL,
                                background='lavender', fg='purple', length=325)
            poultry_slider = Scale(frame1, from_=0, to=15, orient=HORIZONTAL,
                                   background='lavender', fg='purple', length=325)
            pork_slider = Scale(frame1, from_=0, to=15, orient=HORIZONTAL,
                                background='lavender', fg='purple', length=325)
            lamb_slider = Scale(frame1, from_=0, to=15, orient=HORIZONTAL,
                                background='lavender', fg='purple', length=325)
            question_text = Label(frame1, text='Try to get your consumption down by '
                                               '25% by adjusting the '
                                               'sliders', fg='purple',
                                  background='lavender', font=('Helvetica', 18))
            question_text2 = Label(frame1, text='and clicking adjust. Make the number on the '
                                                'right green!', fg='purple', background='lavender',
                                   font=('Helvetica', 18))
            beef_text = Label(frame1, text='Beef: ', fg='purple',
                              background='lavender', font=('Helvetica', 15))
            poultry_text = Label(frame1, text='Chicken: ', fg='purple',
                                 background='lavender', font=('Helvetica', 15))
            pork_text = Label(frame1, text='Pork: ', fg='purple',
                              background='lavender', font=('Helvetica', 15))
            lamb_text = Label(frame1, text='Lamb: ', fg='purple',
                              background='lavender', font=('Helvetica', 15))

            # Sets up various labels and organizes them in the frame
            # similar to earlier blocks of code

            new_result = Label(frame1)

            # Pulls values just like before
            # Okay this where the codes gets a bit weird,
            # because we are deleting a label and replacing it later on,
            # we need to set it up before hand

            global output3
            output3 = ''

            def final() -> None:
                """Shows the user a summation of their results"""

                global root2
                root1.destroy()
                # Creates a new global window whose information
                # can subsequently be accessed by other windows
                # Destroys the change page window

                root2 = Tk()
                root2.title('Meat Monitor')
                root2_x = int((root2.winfo_screenwidth() / 2) - (800 / 2))
                root2_y = int((root2.winfo_screenheight() / 2) - (600 / 2))
                root2.geometry(f'{800}x{600}+{root2_x}+{root2_y}')
                root2.configure(background='lavender')
                # Sets up a new window that exists at the center of the
                # user's screen regardless of resolution

                frame2 = Frame(master=root2, width=750, height=550, background='lavender')
                frame2.pack()

                global graphic3
                png4 = Image.open(
                    f'{cwd}/assets/splash3.png')
                resized_png4 = png4.resize((300, 150), Image.ANTIALIAS)
                graphic3 = ImageTk.PhotoImage(resized_png4)
                graphic_label3 = Label(frame2, image=graphic3, background='lavender')
                graphic_label3.place(x=225, y=0)

                a = [x.weekly_consumption for x in user1.animal_list.values()]
                x = int(user1.total_emissions / 1000)

                b = [x.new_consumption for x in user1.animal_list.values()]
                y1 = int(user1.new_total_emissions / 1000)
                y2 = int(user1.emission_reduction / 1000)

                sum1 = Label(frame2, text=f'In a week, you consume beef {a[0]} '
                                          f'times, chicken {a[1]} times, '
                                          f'pork {a[2]} times, and lamb {a[3]} times,',
                             fg='purple',
                             background='lavender', font=('Helvetica', 15))

                sum2 = Label(frame2, text=f'{user1.name}, your diet produces {x} '
                                          f'kg of CO2 per week.', fg='purple',
                             background='lavender', font=('Helvetica', 20))
                sum3 = Label(frame2,
                             text=f'But, if you change your diet '
                                  f'of beef to {b[0]} times, '
                                  f'chicken to {b[1]} times, pork to {b[2]} times,'
                                  f' and lamb to {b[3]} times,',
                             fg='purple', background='lavender', font=('Helvetica', 15))
                sum4 = Label(frame2, text=f'This saves {y2} Kg of CO2 per week, '
                                          f'producing only {y1} Kg of CO2 per week',
                             fg='purple', background='lavender', font=('Helvetica', 20))
                sum5 = Label(frame2, text='In conclusion, by changing your diet based '
                                          'on all this info,',
                             fg='purple', background='lavender', font=('Helvetica', 20))
                sum6 = Label(frame2, text='You save a large amount of CO2. If '
                                          'everyone in the world were to make ',
                             fg='purple', background='lavender', font=('Helvetica', 20))
                sum7 = Label(frame2, text='such a change, the effects of climate change would be '
                                          'reduced drastically over time',
                             fg='purple', background='lavender', font=('Helvetica', 20))
                sum8 = Label(frame2, text='So we ask you, make a change and do '
                                          'your part in saving the planet!',
                             fg='purple', background='lavender', font=('Helvetica', 20))
                restart1 = Button(frame2, text='Restart', padx=30, pady=10, command=restart,
                                  fg='purple', background='lavender', font=('Helvetica', 15))

                restart1.place(x=600, y=500)
                sum4.place(x=0, y=275)
                sum3.place(x=0, y=225)
                sum2.place(x=0, y=175)
                sum1.place(x=0, y=125)

                sum5.place(x=0, y=350)
                sum6.place(x=0, y=380)
                sum7.place(x=0, y=410)
                sum8.place(x=0, y=440)

            def change() -> None:
                """Changes the label text for the user's new CO2 emissions"""
                user1.create_goals([float(beef_slider.get()), float(poultry_slider.get()),
                                    float(pork_slider.get()), float(lamb_slider.get())])

                user1.goal_stats()
                output2 = int(user1.new_total_emissions / 1000)

                global new_result
                new_result = Label(frame1)
                new_result.destroy()
                # The label we are replacing is set up, and is a global var
                # so we can change its position later
                # We then destroy the label and replace it depending on the elif tree below
                # Pulls values, just like before

                # this is the new carbon footprint the user creates
                # based on the change in their diet

                if user1.emission_reduction_percentage > 25:
                    new_result = Label(frame1, text=output2, fg='green', width=5,
                                       background='lavender', font=('Helvetica', 60))
                elif user1.emission_reduction_percentage > 12.5:
                    new_result = Label(frame1, text=output2, fg='yellow', width=5,
                                       background='lavender', font=('Helvetica', 60))
                else:
                    new_result = Label(frame1, text=output2, fg='red', width=5,
                                       background='lavender', font=('Helvetica', 60))

                new_result.place(x=450, y=165)
                # If the user's carbon footprint is X, or between Y and X,
                # change the colour of the label and show the new value

            def info() -> None:
                """Creates an info page for the User to display relevant
                 statistics on climate change.
                 Preconditions:
                    - len(new_result) != 0
                 """

                root3 = Tk()
                root3.title('Meat Monitor')
                root3_x = int((root3.winfo_screenwidth() / 2) - (500 / 2))
                root3_y = int((root3.winfo_screenheight() / 2) - (500 / 2))
                root3.geometry(f'{500}x{500}+{root3_x}+{root3_y}')
                root3.configure(background='lavender')
                # Sets up a new window identical to the previous one

                frame3 = Frame(master=root3, width=450, height=450, background='lavender')
                frame3.pack()

                text1 = Label(frame3, text='With an average of:', fg='purple',
                              background='lavender', font=('Helvetica', 15))
                text2 = Label(frame3,
                              text=f'{(user1.animal_list["Beef"].weekly_consumption * serving_size_per_animal["Beef"] / 1000)} kg of beef, '
                                   f'{(user1.animal_list["Pork"].weekly_consumption * serving_size_per_animal["Pork"] / 1000)} kg of pork, '
                                   f'{(user1.animal_list["Poultry"].weekly_consumption * serving_size_per_animal["Poultry"] / 1000)} kg of poultry and '
                                   f'{(user1.animal_list["Lamb"].weekly_consumption * serving_size_per_animal["Lamb"] / 1000)} kg of lamb per week',
                              fg='purple',
                              background='lavender', font=('Helvetica', 12))
                text3 = Label(frame3,
                              text=f'{int(user1.total_emissions / 1000)} kg/week '
                                   f'of CO2 is produced to sustain your current meat consumption!',
                              fg='purple', background='lavender', font=('Helvetica', 12))
                text4 = Label(frame3,
                              text=f'This means that your total emissions are '
                                   f'{int(100 + user1.total_emissions_percentage)} '
                                   f'% of the average person in your country',
                              fg='purple', background='lavender', font=('Helvetica', 12))
                text5 = Label(frame3, text='Even though you are consuming less than the average'
                                           ' person in your country,',
                              fg='purple', background='lavender', font=('Helvetica', 12))

                if user1.total_emissions_percentage > 25:
                    text6 = Label(frame3, text='This is a warning that you could be '
                                               'eating too much meat!',
                                  fg='purple', background='lavender', font=('Helvetica', 12))
                    text7 = Label(frame3, text='Meat consumption is one of the '
                                               'main contributors to climate change',
                                  fg='purple', background='lavender', font=('Helvetica', 12))
                    text8 = Label(frame3, text='as breeding the livestock that we eat '
                                               'requires a lot of resources!',
                                  fg='purple', background='lavender', font=('Helvetica', 12))
                    text9 = Label(frame3, text='Reducing meat consumption reduces CO2 emissions, '
                                               'fighting climate change', fg='purple',
                                  background='lavender', font=('Helvetica', 12))
                    text10 = Label(frame3, text='Your diet choices are a key factor '
                                                'in affecting these numbers!',
                                   fg='purple', background='lavender', font=('Helvetica', 15))
                    text11 = Label(frame3, text='Remember to eat all of your food!',
                                   fg='purple', background='lavender', font=('Helvetica', 15))
                    text12 = Label(frame3, text='Every year, 1.3 billion tons of food is wasted.',
                                   fg='purple', background='lavender', font=('Helvetica', 15))

                else:
                    text6 = Label(frame3, text='Facts:', fg='purple',
                                  background='lavender', font=('Helvetica', 16))
                    text7 = Label(frame3, text='- Livestock rearing and meat '
                                               'processing are responsible for approximately',
                                  fg='purple', background='lavender', font=('Helvetica', 12))
                    text8 = Label(frame3, text='30% of the world’s greenhouse gas emissions!',
                                  fg='purple', background='lavender', font=('Helvetica', 12))
                    text9 = Label(frame3, text='- Animal agriculture is responsible '
                                               'for 18% of all greenhouse gases, ',
                                  fg='purple', background='lavender', font=('Helvetica', 12))
                    text10 = Label(frame3, text='whereas industry is responsible for 13%.',
                                   fg='purple', background='lavender', font=('Helvetica', 12))
                    text11 = Label(frame3, text='Your diet choices are a key factor '
                                                'in affecting these numbers!',
                                   fg='purple', background='lavender', font=('Helvetica', 15))
                    text12 = Label(frame3, text='Remember to eat all of your food!',
                                   fg='purple', background='lavender', font=('Helvetica', 15))
                    text13 = Label(frame3, text='Every year, 1.3 billion tons of food is wasted.',
                                   fg='purple', background='lavender', font=('Helvetica', 15))
                    text13.place(x=0, y=375)

                text1.place(x=0, y=25)
                text2.place(x=0, y=50)
                text3.place(x=0, y=75)
                text4.place(x=0, y=100)
                text5.place(x=0, y=125)
                text6.place(x=0, y=150)
                text7.place(x=0, y=175)
                text8.place(x=0, y=200)
                text9.place(x=0, y=225)
                text10.place(x=0, y=250)
                text11.place(x=0, y=300)
                text12.place(x=0, y=325)

            new_result = Label(frame1, text=output3, fg='purple',
                               background='lavender', font=('Helvetica', 60))
            change = Button(frame1, text='Adjust', padx=30, pady=10,
                            command=change, background='lavender', font=('Helvetica', 15))
            graph = Button(frame1, text='View Graphical Analysis', padx=30, pady=10, command=graph,
                           background='lavender', font=('Helvetica', 15))
            next1 = Button(frame1, text='Next', padx=30, pady=10, command=final,
                           background='lavender', font=('Helvetica', 15))
            info = Button(frame1, text='Info', padx=30, pady=10, command=info,
                          background='lavender', font=('Helvetica', 15))
            # Sets up the label that the user sees on upon the start of the window,
            # it will always be 0.0 in purple
            # This gets overwritten every time the function change is called,
            # basically when change button is pressed
            # Sets up buttons

            text.place(x=120, y=125)
            result.place(x=175, y=165)
            beef_slider.place(x=250, y=330)
            poultry_slider.place(x=250, y=380)
            pork_slider.place(x=250, y=430)
            lamb_slider.place(x=250, y=480)

            question_text.place(x=100, y=265)
            question_text2.place(x=120, y=290)
            beef_text.place(x=170, y=350)
            poultry_text.place(x=170, y=400)
            pork_text.place(x=170, y=450)
            lamb_text.place(x=170, y=500)

            new_result.place(x=450, y=200)
            change.place(x=150, y=540)
            graph.place(x=250, y=540)
            next1.place(x=460, y=540)
            info.place(x=550, y=540)
            # Organizes the location of each element in the frame

    start = Button(root, text='Submit', padx=30, pady=10, command=write,
                   background='lavender', font=('Helvetica', 15))
    # Creates a button to start the calculation and produce results on a new window
    graphic_label1.place(x=225, y=0)
    e_beef.place(x=350, y=205)
    e_poultry.place(x=350, y=255)
    e_pork.place(x=350, y=305)
    e_lamb.place(x=350, y=355)
    e_name.place(x=350, y=425)
    drop.place(x=350, y=475)

    question.place(x=75, y=135)
    question2.place(x=90, y=165)
    q_beef.place(x=200, y=225)
    q_poultry.place(x=200, y=275)
    q_pork.place(x=200, y=325)
    q_lamb.place(x=200, y=375)
    q_name.place(x=200, y=425)
    q_country.place(x=200, y=475)

    start.place(x=330, y=525)
    # Organizes the location of each element in the frame


# All elements in the splash page/home page are here
# Not in a definition because it needs to execute as
# soon as the file is run, without any user input
# Rest of this code is standard window set up, as seen in the code above

splash_root = Tk()
splash_root.title('Meat Monitor')
splash_x = int((splash_root.winfo_screenwidth() / 2) - (800 / 2))
splash_y = int((splash_root.winfo_screenheight() / 2) - (600 / 2))
splash_root.geometry(f'{800}x{600}+{splash_x}+{splash_y}')
splash_root.configure(background='lavender')
splash_root.after(6000, inputs)

png1 = Image.open(f'{cwd}/assets/splash3.png')
resized_png1 = png1.resize((600, 300), Image.ANTIALIAS)
splash_logo = ImageTk.PhotoImage(resized_png1)

logo_label1 = Label(image=splash_logo, background='lavender')
logo_label1.pack(pady=100)

mainloop()

# if __name__ == '__main__':
#     import python_ta
#
#     python_ta.check_all(config={
#         'extra-imports': ['python_ta.contracts'],
#         'allowed-io': ['run_example_break'],
#         'max-line-length': 100,
#         'disable': ['R1705', 'C0200']
#     })
#
#     python_ta.contracts.check_all_contracts()
#     import doctest
#
#     doctest.testmod()
