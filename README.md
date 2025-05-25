# splice

![](./logo.png)

## What?

A single process, in-memory message queue written in python. Main features are:
* Very simple API
* Fast
* Uncomplicated
* Fan-out / Fan-in
* Back-pressure is built in

## Why?

Because I wanted the most simplistic API (subjectively) I could possibly think of for processing real-time data from multiple sources and to multiple sinks.

## How ?

By re-using the concept of `Key Expression`s from `Zenoh` and utilizing in-memory storage for a very simplistic implementation of a message queue that has the following features

## Usage

