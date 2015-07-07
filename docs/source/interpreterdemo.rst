interpreter module demo
=======================

Initial Setup
------------------------------------------
.. include:: known_actions.txt
   :literal:

Each line in this input file represents one **action set**. All actions in the a synonym set are recognized as having the same meaning (they are known as synonyms), and will be interpreted and executed by LILI in the same exact way. For example, *show* and *teach* are synonyms, so the commands *Show me how to wash my hands* and *Teach me how to wash my hands* are exactly the same to LILI.

Each action set has an index value (referred to as the **action set index**), which is simply the line number the set is found on minus 1. The action set index of the action set *[move, go]* is 0, the index of *[turn, twist, rotate]* is 1, and so on.

.. testsetup:: *

   import interpreter.interpreter as interp

The following code generates two important data structures in the interpretation task. The first is the list of known actions, which is a list of tuples containing the action along with its action set index. The other is a list of **object extractor functions**, which are functions that pick out key words (known as **objects**) from the command and label them with semantic tags, thus indicating how LILI should interact with each object.

.. testcode::

   res = interp.build_action_structures("./source/known_actions.txt")
   known_actions = res[0]
   print known_actions

   object_extractor_functions = res[1]
   funcs = [func.__name__ for func in object_extractor_functions]
   print funcs

The first line of output shows the contents of the known actions list. Each element in that list is a tuple of the form (*action*, *action_set_index*). It is important to note that the *action* is only used to pick words out of the command, whereas the *action_set_index* gives actual meaning to the action.

The second line of output shows the name of each function in the object extractor function list. The actual function is stored as an object in the list *object_extractor_functions*, but a list of the names are printed as output here for readability. Therefore, each individual function can be called later on by indexing that array like so: ``object_extractor_functions[<index>](<params>)``.

Notice that the action set index of each known action corresponds to the appropriate object extractor. For example, the object extractor for *talk*, *speak*, and *tell* are in the action set with an index of 4 and their object extractor can be accessed at index 4 (the 5th element) of ``object_extractor_functions``.

Also notice that the name of the extractor functions begin with "object_dict\_" and end with the first action of its corresponding action set. This concept is important to maintainability of the system. When new action sets are added to the input file, their indices are generated automatically, and the extractor functions are automatically placed in the correct order, as long as the first action of each set matches the suffix of the corresponding extractor function. Thus, the maintainer does not need to be concerned with the order of function declarations or lines in the input file.

.. testoutput::

   [('follow', 3), ('go', 0), ('move', 0), ('rotate', 1), ('show', 5), ('speak', 4), ('stop', 2), ('talk', 4), ('teach', 5), ('tell', 4), ('turn', 1), ('twist', 1)]
   ['object_dict_move', 'object_dict_turn', 'object_dict_stop', 'object_dict_follow', 'object_dict_talk', 'object_dict_show']

Preprocessing and Action Detection
-----------------------------------

The following code simply preprocesses a raw text command, which currently only involves tokenizing it.

.. testcode::

   sent_text = "Teach me how to wash my hands"
   sent = interp.preprocess_text(sent_text)
   print sent

.. testoutput::

   ['Teach', 'me', 'how', 'to', 'wash', 'my', 'hands']

The following code searches through each token (from first to last) to see if any of the words match an action in the known actions list built in the section above.

.. testcode::

   action_tuple = interp.extract_action(sent, known_actions)
   print action_tuple

.. testoutput::

   (5, 0)

The output of this search is a tuple containing the found action's set index along with its position in the sentence in the format (*action_set_index*, *position_in_sent*). The action detected in the given sentence *Show me how to wash my hands* is *show*, which is part of the action set with index 5, grouped with the action *teach*. Also, its position in the sentence is the first word, so its position index is 0. This function would yield the same exact output if it was given the sentence *Teach me how to wash my hands*.

Extracting Objects from the Command
------------------------------------

The following code extracts the objects from the rest of the command, since the action has been extracted in the previous section. The action set index determines which object extractor function will be applied to the rest of the command, and thus what set of rules are going to be used to extract the objects. Since the action is *teach*, the first action in its action set is *show*, and thus the appropriate object extractor function for this command is ``object_dict_show()``, which is called by indexing the ``object_extractor_functions`` list inside of the ``interp.generate_object_dict()`` function.

.. testcode::

   object_dict = interp.generate_object_dict(sent, action_tuple, object_extractor_functions)

   # Print dictionary values in same order every time
   print "person: " + object_dict["person"]
   print "show_action: " + object_dict["show_action"]
   print "object: " + object_dict["object"]
   print "video_title: " + object_dict["video_title"]

.. testoutput::

   person: me
   show_action: wash
   object: hands
   video_title: wash-hands

The above output simply displays the values of the objects along with their keys as stored in the resulting **object dictionary**, which is a Python *dict* structure that maps objects to semantic labels. The keys are essentially semantic labels that can be given to the LILI master control module to execute the appropriate action. The resulting object dictionary can be sent to another software component as a JSON string or a Python *dict*.

See the