# AI-Traffic-Lights-Controller

By Yossi Doctor, Adi Borochov, Nimrod Alon, Nadav Alon

## What problem are you going to solve?

We aim to design an AI traffic lights controller to optimize and ensure better traffic flow using optimal light
switching behavior.

## How are you going to solve it?

We will use two approaches: reinforcement learning and search.

## Why do you think that your approach is the right one?

Given a rush-hour traffic stream, the main goal of the AI traffic lights controller is to let all the cars pass as
quickly as possible while avoiding collisions.
With reinforcement learning, the agent can be rewarded and penalized based on predetermined rules, such as priority of
passage for emergency vehicles, making it learn to solve the problem.
With search, the agent can be pointed using heuristics toward the final state of no traffic.
These two approaches allow the AI controller to calculate the optimal switching behavior for the traffic lights to
shorten waiting times at junctions and reduce journey times.

## How are you going to test your results?

Using a traffic flow simulator, we will measure the average waiting and journey times and compare them at different
stages of the learning process.
