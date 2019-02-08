* Don't do heavy initializing in `__init__`
    * It should be best done as a client that is passed in as a worker global
    * If you have to, override the `pre_work` method
* Have a steady `_id` passed to `BaseWorker`