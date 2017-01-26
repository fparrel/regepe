//Header
const LANG='{{_("en")}}';
const SEARCHING='{{_("Searching...")}}';
const SEARCH_RESULTS_TABLE_BEGIN='{{_("<h1>Search results</h1><table id=\"search_results_table\"><thead><tr><th id=\"sortby_date\">Date</th><th id=\"sortby_desc\">Description</th><th id=\"sortby_user\">User</th><th>Preview</th></tr></thead><tbody id=\"search_tbody\">")|replace("'","\\'")}}';
const SEARCH_RESULTS_TABLE_END='{{_("</tbody></table>")}}';
const NO_MAP_FOUND='{{_("<b>No map found</b><br/>")}}';
const LOGGED_AS='{{_("Logged as")}}';
const LOGOUT='{{_("Logout")}}';
const LOGIN_FAILED='{{_("Login failed: ")}}';
const SESSION_EXPIRED='{{_("Session expired, please re-login<br/>")}}';
const LOGGING='{{_("Logging... ")}}';
const HEADER_LOGIN_INIT="{{_("<form>User: <input id=\"login_user\" name=\"user\" type=\"text\"/>Password: <input id=\"login_password\" name=\"password\" type=\"password\"/><input type=\"button\" value=\"Login\" onclick=\"onLoginClick();\"/><br/><a href=\"/registerform\">Register</a> | <a href=\"/forgotpwd\">Forgot password?</a></form>")|replace("\"","\\\"")}}";
const KNOTS='{{_("knots")}}';
const SSW='{{_("SSW")}}';
const SW='{{_("SW")}}';
const WSW='{{_("WSW")}}';
const W='{{_("W")}}';
const WNW='{{_("WNW")}}';
const NW='{{_("NW")}}';
const NNW='{{_("NNW")}}';
const TRACK='{{_("Track")}}';

//Prepare+common prepare&map
const MARKS='{{_("Marks")}}';
const EXPORT='{{_("Export")}}';
const WAYPOINTS='<b>{{_("Waypoints")}}</b>';
const CLEAR_TRACK="{{_('Clear track?')}}";
const SELECTION="{{_('Selection')}}";
const DIST="{{_('Dist: ')}}";
const VERT_DST="{{_('Vert dst:')}}";
const SLOPE="{{_('Slope:')}}";
const CURRENT_POINT="{{_('Current point:')}}";
const ELE="{{_('Ele:')}}";

//Submitform
const UPLOADING_FILE='{{_("Uploading file...")}}<br/>';
const SELECT_TRACK='{{_("File contains several tracks. Select a track: ")|replace("'","\\'")}}';
const GEOPORTAL_FRANCEONLY="{{_('Geo Portal (France only)')}}";
const HIKING="{{_('Hiking, Skitouring, Ski, Snowboard, Bike')}}";
const KAYAK="{{_('Surfing, Sea Kayak, Motor boat')}}";
const KITE="{{_('Windsurf, Kite, Sailing')}}";
const SNOWKITE="{{_('Snowkite, Free-flying, Air Balloon')}}";

//Userhome
const CONFIRM_DELETION_OF="{{_('Confirm deletion of ')}}";
const MAPS="{{_(' map(s)?')}}";
