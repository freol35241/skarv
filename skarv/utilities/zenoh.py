import zenoh

from .. import put, get


def mirror(zenoh_session: zenoh.Session, zenoh_key: str, skarv_key: str):
    """Mirror a Zenoh key expression to a Skarv key.

    Subscribes to the Zenoh key expression and automatically puts received values into Skarv.
    If the Zenoh key already has a value, it fetches and stores it in Skarv (if not already present).

    Args:
        zenoh_session (zenoh.Session): The Zenoh session to use.
        zenoh_key (str): The Zenoh key expression to subscribe to.
        skarv_key (str): The Skarv key to store values in.
    """
    # Subscribe to the key expression and put the received value into skarv
    zenoh_session.declare_subscriber(
        zenoh_key, lambda sample: put(skarv_key, sample.payload)
    )

    # If the key expression already has a value, we fetch it and put it into skarv
    for response in zenoh_session.get(zenoh_key):
        if (ok_response := response.ok) and not get(skarv_key):
            put(skarv_key, ok_response.payload)
