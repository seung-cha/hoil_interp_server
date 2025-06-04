$func_decl %fibonacci% $real $param %x% $real 
$open_scope
$branch_begin
$if %x%;1;==
$open_scope
$return 1
$close_scope
$if_end
$elif %x%;0;<=
$open_scope
$return 0
$close_scope
$elif_end
$branch_end
$return $,%fibonacci%,%x%;2;-$^;$,%fibonacci%,%x%;1;-$^;+
$close_scope
$func_decl_end
$decl %number% $real 7
$decl %result% $real $,%fibonacci%,%number%$^
$call %Print% "{number}th Fibonacci Number is {result}"
$decl %i% $real 0
$while %i%;5;<=
$open_scope
$call %Print% "Repeating statement: {i} times"
$decl %i% $real %i%;1;+
$close_scope
$while_end

