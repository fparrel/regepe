
def FormGetFile(form):
    if not form.has_key('gpx_file'):
        return None
    if not form['gpx_file'].file:
        return None
    if form['gpx_file'].filename=='':
        return None
    return form['gpx_file'].file

def FormParseBool(form,input_name):
	#if not form.has_key(input_name):
	#	raise Exception("Error on form submit: <i>%s</i> not found" % input_name)
	return (form.getvalue(input_name)=='yes');

def FormParseInt(form,input_name):
	if not form.has_key(input_name):
		raise Exception("Error on form submit: <i>%s</i> not found" % input_name)
	return int(form.getvalue(input_name));

def FormParseFloat(form,input_name):
	if not form.has_key(input_name):
		raise Exception("Error on form submit: <i>%s</i> not found" % input_name)
	return float(form.getvalue(input_name));

def FormParseStr(form,input_name):
	if not form.has_key(input_name):
		raise Exception("Error on form submit: <i>%s</i> not found" % input_name)
	return str(form.getvalue(input_name));

def FormParse(form,input_name,fieldtype):
	if (fieldtype==bool):
		return FormParseBool(form,input_name)
	elif (fieldtype==int):
		return FormParseInt(form,input_name)
	elif (fieldtype==float):
		return FormParseFloat(form,input_name)
	elif (fieldtype==str):
		return FormParseStr(form,input_name)
	return None

def FormParseOptions(form,_options):
    for key in _options:
        if form.has_key(key):
            _options[key] = FormParse(form,key,type(_options[key]))
