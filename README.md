# DiceRoller

The main class which does message handling is dnd.py, to start this a Discord Bot Token must be supplied to the run command at the end of the file

The Discord.py library uses asynchronous python to allow for multiple messages to be handled simeltaneously. This doesn't affect much here as the majority of the code is the equivalent of static. The fudging of rolls (allowing an admin to push rolls towards a region of likelihood) is not thread safe, but this is unlikely to be an issue unless high throughput is required.

The diceparser handles the majority of the complexity of project. Compiler tools are used here, with a lexical analysis tool and parser being used. Ply.lex and Ply.yacc are the libraries used for these.
The input string is run through the lexer which uses regex to separate it into tokens, which are then passed into the parser which decides on how to interpret different tokens.