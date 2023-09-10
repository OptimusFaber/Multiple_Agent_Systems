# **Multiple agent service**

**Example with couriers and orders**

field 200x200

![version_1](https://github.com/rodion02/Multiple_Agent_Systems/blob/main/example.gif)

(here couriers are choosing 1 order for each one and start working)

Then I decided to improve my Couriers, I made them list of orders, like a schedule.
Now my algorithm helps them find new orders to increase my income.

![version_2](https://github.com/rodion02/Multiple_Agent_Systems/blob/main/example2.gif)

But unfortunately, this is not the most optimal algorithm. 
Greedy algorithm is kind of stupid, he picks everything that looks fancy and don't look forward. 
As common in all companies if something goes wrong - you have to pay for it. Here we have the same situation.
``higgle_algorithm`` picks all the orders which weren't received and gives it to the Couriers who can deliver it ASAP.
And this is why I keep loosing money. I'm still in profit, but it could be bigger.
