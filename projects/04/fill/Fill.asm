// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
@SCREEN
D=A
@addr
M=D
D=M
@8160
D=D+A
@til
M=D
@i
M=0
@isfill
M=0
(LOOP)
  @SCREEN
  D=A
  @addr
  M=D
  D=M
  @scr
  M=D
  @KBD
  D=M
  @kbd
  M=D
  @FILL
  D;JGT
  @DELL
  0;JMP
(FILL)
  @isFILL
  M=-1
  @DISPLAY
  0;JMP
(DELL)
  @isFILL
  M=0
  @DISPLAY
  0;JMP
(DISPLAY)
  @isFILL
  D=M
  @scr
  A=M
  M=D
  @scr
  M=M+1
  @KBD
  D=M
  @kbd
  D=D-M
  @LOOP
  D;JNE
  @scr
  D=M
  @til
  D=D-M
  @LOOP
  D;JGE
  @DISPLAY
  0;JMP
(END)
  @END
  0;JMP
