$func_decl %fibonacci% $real $param %num% $real 
$open_scope
$branch_begin
$if %num%;1;==
$open_scope
$return 1
$close_scope
$if_end
$elif %num%;0;<=
$open_scope
$return 0
$close_scope
$elif_end
$branch_end
$return $,%fibonacci%,%num%;2;-$^;$,%fibonacci%,%num%;1;-$^;+
$close_scope
$func_decl_end
$decl %result% $real $,%fibonacci%,8$^
$call %Print% "8th fibonacci number is {result}"

