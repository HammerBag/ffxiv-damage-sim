# ffxiv-damage-sim
Damage Simulator for FFXIV

This is a work in progress but will eventually be a web-based simulator for FFXIV to calculate expected damage output using established formulas and rotations. Currently, this is a python applet that will run in a console.

Current development is in a container on repl.it (allows me to access it at work so I can do more on my lunch breaks, but has some limitations). Uses a replit package to keep the console commands clear. When running, you would need to remove the "import replit" and instances of replit.clear() or you will get errors.

## ChangeLog/Updates

**July 20, 2018** -   

Haven't updated this in a little while. I've been working on some back-end modules in handling the xivdb API (the data output is huge, so trying to find a short, dynamic method to break it down into the info I need, so that the available gear stays current with current patches). Here's a summary of where the program is at:
* Most of the basic structure has been completed. There are still a lot of empty job classes. I was thinking that would be the best way to handle rotations, but now I'm not actually so sure. They'll stay there for now.
* The Menu is mostly functional. Not every command *does* anything right this moment, but the general structure is there, although working still to condense it, as probably some menus can be handled with conditional arguments rather than a fully separate function.

## Planned Features/Roadmap

* __*completed*__ - Import the damage formulas used in the game. Grabbed all the formulas from "How to be a Math Wizard". Have tested the formulas/damage calculation and it works as expected.
* __*completed*__ - Design the console menu -- This will be crucial for testing until I can implement a web/gui interface.
* __*In Progress*__ - Connect app with XIVDB, to allow the user to import gear from their character ID, and eventually pull a list of gear to use
* - Develop Web Interface - Still working on mocking up designs. Probably will create this with Ruby on the Rails, or possibly try a direct python web interface.
* Simulate based on rotation - Instead of simulating a single hit, the program would run a dummy simulation (basically Stone-Sky-Sea, but allow for longer durations)
* Simulate dummy parse with a full party - This is a **Major** stretch goal, but if implemented could be useful in helping parties align their buffs
