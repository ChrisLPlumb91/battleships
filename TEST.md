# Testing

I tested two aspects of this program
<ul>
    <li>How it handles invalid input from the user</li>
    <li>How it interacts with the spreadsheet to which it is linked</li>
</ul>
<br>
<hr>

<strong><h2>Invalid input testing</h2></strong>
<hr>
There are 5 different sections in this program that request input from the user:
<ul>
    <li>The selection of the size of the grid</li>
    <li>The quit sequence that follows if you provide 0 as the grid size</li>
    <li>The setting of the starting coordinates for each ship</li>
    <li>The guessing phase</li>
    <li>The play again sequence that follows once the user win or lose</li>
</ul>

For each of these, I tested many different kinds of input.
<br>
<br>

<strong><h3>Grid size selection inputs tested</h3></strong>
<ul>
    <li>10</li>
    <li>12</li>
    <li>14</li>
    <li>0</li>
    <li>A number other than the 4 above</li>
    <li>A letter</li>
    <li>A punctuation mark</li>
    <li>A number 2+ digits in length</li>
    <li>A string of letters</li>
    <li>A string of punctuation marks</li>
    <li>Nothing, i.e. pressing Enter without typing anything</li>
</ul>

None of the above inputs produced any errors.
<br>
<br>

<strong><h3>Early quit inputs tested</h3></strong>
<ul>
    <li>Y</li>
    <li>N</li>
    <li>Lowercase y</li>
    <li>Lowercase n</li>
    <li>A letter other than Y or N</li>
    <li>YY</li>
    <li>NN</li>
    <li>A number</li>
    <li>A punctuation mark</li>
    <li>A number 2+ digits in length</li>
    <li>A string of letters</li>
    <li>A string of punctuation marks</li>
    <li>Nothing, i.e. pressing Enter without typing anything</li>
</ul>

Other than Y and N (and their lowercase versions), the other inputs initially caused the program to go into an infinite loop, as I had accidentally placed the input method before and outside of the while loop.
<br>
<br>

<strong><h3>Ship coordinate setting inputs tested</h3></strong>
The below tests were done for each of the 7 ships that the user must position, and also for each of the three grid sizes.

<ul>
    <li>1-digit number</li>
    <li>2-digit number</li>
    <li>3-digit number</li>
    <li>1 letter</li>
    <li>2 letters without a space</li>
    <li>3 letters without a space</li>
    <li>1 punctuation mark</li>
    <li>2 punctuation marks without a space</li>
    <li>3 punctuation marks without a space</li>
    <li>3 numbers with spaces</li>
    <li>2 letters with spaces</li>
    <li>3 letters with spaces</li>
    <li>2 punctuation marks with spaces</li>
    <li>3 punctuation marks with spaces</li>
    <li>1 number and 1 letter with a space</li>
    <li>1 number and 2 letters with spaces</li>
    <li>2 numbers and 1 letter with spaces</li>
    <li>1 number and 1 punctuation mark with a space</li>
    <li>1 number and 2 punctuation marks with spaces</li>
    <li>2 numbers and 1 punctuation mark with spaces</li>
    <li>1 letter and 1 number with a space</li>
    <li>1 letter and 2 numbers with spaces</li>
    <li>2 letters and 1 number with spaces</li>
    <li>1 letter and 1 punctuation mark with a space</li>
    <li>1 letter and 2 punctuation marks with spaces</li>
    <li>2 letters and 1 punctuation mark with spaces</li>
    <li>1 punctuation mark and 1 number with a space</li>
    <li>1 punctuation mark and 2 numbers with spaces</li>
    <li>2 punctuation marks and 1 number with spaces</li>
    <li>1 punctuation mark and 1 letter with a space</li>
    <li>1 punctuation mark and 2 letters with spaces</li>
    <li>2 punctuation marks and 1 letter with spaces</li>
    <li>Number-letter-number with spaces</li>
    <li>Number-punctuation mark-number with spaces</li>
    <li>Letter-number-letter with spaces</li>
    <li>Letter-punctuation mark-letter with spaces</li>
    <li>Punctuation mark-number-punctuation mark with spaces</li>
    <li>Punctuation mark-letter-punctuation mark with spaces</li>
    <li>Number-letter-punctuation mark with spaces</li>
    <li>Number-punctuation mark-letter with spaces</li>
    <li>Letter-number-punctuation mark with spaces</li>
    <li>Letter-punctuation mark-number with spaces</li>
    <li>Punctuation mark-number-letter with spaces</li>
    <li>Punctuation mark-letter-number with spaces</li>
    <li>All of the above but preceded by a single space</li>
    <li>Nothing, i.e. pressing Enter without typing anything</li>
    <li>A number that positions the ship outside of the selected grid, e.g. 1 12 H on a 10x10 grid</li>
    <li>A valid horizontal position</li>
    <li>A valid vertical position</li>
    <li>A valid diagonally left and down position</li>
    <li>A valid diagonally right and down position</li>
</ul>

Many of these tests revealed minor issues with my error messages. Certain of them weren't specific enough, and others were being triggered instead of the ones that were more relevant. I fixed these issues by rearranging the decision structures containging these messages and adding more information to / rephrasing the messages themselves. 
<br>
<br>

<strong><h3>Ship coordinate guessing inputs tested</h3></strong>

For this part of the game, I used the same battery of tests as I did for the selection phase. I did this only for a single guess, but for all three grid sizes.

I also played several games, checking to make sure that the following where happening when they should have been:
<ul>
    <li>That ships were sinking when all their parts had been hit</li>
    <li>That it was not possible to hit ship parts which had already been hit</li>
</ul>

I checked both of the above for both the player and the CPU, and thankfully, no issues arose.
<br>
<br>

<strong><h3>Play again inputs tested</h3></strong>
[see inputs for early quit]
<br>
<br>
<hr>

<strong><h2>Spreadsheet interaction</h2></strong>
<hr>

The program interacts with 2 different sheets within a Google Sheet - the 'player' and 'cpu' sheets. The 'player' sheet is populated with the player's ships before the game begins, and the CPU's ships are gradually revealed on the 'cpu' as the player successfully lands hits.

To test this functionality, I did a number of things:
<ul>
    <li>I entered valid coordinates.</li>
    <li>I entered starting coordinates within the grid boundaries that, because of the given ship's size and orientation, would cause it to poke out of the grid.</li>
</ul>

For both the vertical and horizontal ships, no issues arose, but due to logical errors in the algorithms I wrote for the two diagonal orientations, diagonal ships placed at the edges of the grid would either 1. simply cut short at the bottom edge, or 2. move to the far side of the next row down, and continue from there (e.g. one half would be on the far right edge of the grid, and another half would be on the far left).

These issues plagued both the player and user spreadsheets, in fact, despite the fact that the code for populating them is quite different. However, I managed to resolve the issue for both by essentially telling the program to treat any ships that exhibit this behaviour as being out of bounds.