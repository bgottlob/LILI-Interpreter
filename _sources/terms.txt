Terminology
============

.. _action:

:index:`action`
   A verb that corresponds to a single task that LILI can complete. For example, the action *follow*, as in the command *"Follow me to the kitchen"*, tells LILI to follow someone.

.. _action-set:

:index:`action set`
   A group of :ref:`actions <action>` that have the same meaning to the interpreter. For example, the actions *turn*, *twist*, and *rotate* comprise an action set. These three actions can be used interchangeably in the same command. The commands *"Turn right"*, *"Twist right"*, and *"Rotate right"* will all be interpreted as the same command, all yielding the same output from LILI.

.. _action-set-index:

:index:`action set index`
   A positive (or zero) integer value that uniquely identifies an :ref:`action set <action-set>`.

.. _object:

:index:`object`
   A key word that must be interpreted in order for LILI to perform the correct task. In the command *"Follow me"*, *follow* is the :ref:`action <action>` and *me* is an object because LILI must know who to follow in order to do that task as the user intends.

.. _object-dictionary:

:index:`object dictionary`
   A dictionary, a set of key-value pairs, that maps a set of :ref:`objects <object>` to semantic labels that correspond to the context and meaning of each object. In the command *"Follow me"*, *me* is stored as a value in an object dictionary whose key is *person*.

.. _object-extractor-function:

:index:`object extractor function`
   A function that uses predetermined rules to extract :ref:`objects <object>` from commands, tags the objects with semantic labels, and generates an :ref:`object dictionary <object-dictionary>`.