# ffxiv-damage-sim
Damage Simulator for FFXIV

This is a work in progress but will eventually be a web-based simulator for FFXIV to calculate expected damage output using established formulas and rotations.

Current development is in a container on repl.it (allows me to access it at work so I can do more on my lunch breaks, but has some limitations). Uses a replit package to keep the console commands clear. When running, you would need to remove the "import replit" and instances of replit.clear() or you will get errors.

__**ChangeLog/Updates**__
__July 20, 2018__ - 
Haven't updated this in a little while. I've been working on some back-end modules in handling the xivdb API (the data output is huge, so trying to find a short, dynamic method to break it down into the info I need, so that the available gear stays current with current patches). Here's a summary of where the program is at:
* Most of the basic structure has been completed. There are still a lot of empty job classes. I was thinking that would be the best way to handle rotations, but now I'm not actually so sure. They'll stay there for now.
* The Menu is mostly functional. Not every command *does* anything right this moment, but the general structure is there, although working still to condense it, as probably some menus can be handled with conditional arguments rather than a fully separate function.


