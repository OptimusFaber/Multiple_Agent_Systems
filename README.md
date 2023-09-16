# **Multiple agent service**

**Example with couriers and orders**

# **Version 1**

field 200x200

![version_1](https://github.com/rodion02/Multiple_Agent_Systems/blob/main/example.gif)

(here couriers are choosing 1 order for each one and start working)


# **Version 2**

field 200x200

Then I decided to improve my Couriers, I made them list of orders, like a schedule.
Now my algorithm helps them find new orders to increase my income.

![version_2](https://github.com/rodion02/Multiple_Agent_Systems/blob/main/example2.gif)

But unfortunately, this is not the most optimal algorithm. 
Greedy algorithm is kind of stupid, he picks everything that looks fancy and don't look forward. 
As common in all companies if something goes wrong - you have to pay for it. Here we have the same situation.
``higgle_algorithm`` picks all the orders which weren't received and gives it to the Couriers who can deliver it ASAP.
And this is why I keep loosing money. I'm still in profit, but it could be bigger.

# **Version 3**

Then I decided to change my algorithm of route-making and a little changed ```greedy_algorithm3```.
Now if my program cannot find the best Courier for the Order, it just picks the most close and free one.
Also, I cleaned my code and added some new features and connected it with PyGame, and here is the result:

field 600x600

![version_3](https://github.com/rodion02/Multiple_Agent_Systems/blob/main/example3.gif)