# skarv

> **skarv** is a Swedish noun that refers to the point where two things are joined together. Translations to English includes joint, splice, connection and similar words. Interestingly, it is also the swedish word for cormorant (the bird).

## What?

A simple, synchronous, thread-safe, single process, in-memory message "broker" written in python. 

## Why?

Because I wanted the most simplistic API (subjectively) I could possibly think of for processing real-time data from multiple sources to multiple sinks via any intermediate processing setup.

## How ?

By re-using the concept of [`Key Expression`](https://github.com/eclipse-zenoh/roadmap/blob/main/rfcs/ALL/Key%20Expressions.md)s from [`Zenoh`](https://zenoh.io/) and utilizing in-memory storage for a very simplistic implementation of a message "broker" that supports the following operations:
* Putting data to the broker
* Subscribing to data from the broker
* Getting the latest data from the broker

## Usage

Docs are available at https://freol35241.github.io/skarv

```python

import skarv

@skarv.subscribe("any/**")
def _(sample: skarv.Sample):
    print(sample.key_expr)
    print(sample.value)

skarv.put("any/thing", 42)

samples = skarv.get("any/**")

print(samples)
```

## Installation

```
pip install skarv
```

## License

Apache 2.0 - see [LICENSE](LICENSE) file for details.
