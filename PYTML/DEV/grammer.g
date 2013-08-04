grammar PYTML;
 
options{
     language=Python;
}
 
/*------------------------------------------------------------------
 * PARSER RULES
 *------------------------------------------------------------------*/
 
tagdef : NAME attrs suite;

attrs : attr+ ':';
attr : NAME '=' STRING;


stmt : simple_stmt
     | tagdef
     ;

simple_stmt : STRING (';' STRING)* [';'] NEWLINE;

suite : simple_stmt
      | NEWLINE INDENT stmt+ DEDENT
      ;
