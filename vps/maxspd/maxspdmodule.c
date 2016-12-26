#include <Python.h>
#include <stdio.h>

static PyObject *
maxspd_tst(PyObject *self, PyObject *args)
{
	// test, not working
	int i, *j, **t;
	PyArg_ParseTuple(args, "((i:)#:)#", &t, &j, &i);
	int a,b;
	for(a=0; a<i; a++)
		for(b=0; b<j[i]; b++)
			printf("%d, ", t[a][b]);
   printf("\n");
}

static PyObject *
maxspd_compute(PyObject *self, PyObject *args)
{
	PyObject *objtms,*objdsts,*objeles;
	int sts;

    if (!PyArg_ParseTuple(args, "OO|O", &objtms,&objdsts,&objeles))
        return NULL;
	int ltms = PyList_Size(objtms);
	int ldsts = PyList_Size(objdsts);
	if(objeles!=NULL) {
		int leles = PyList_Size(objeles);
		if(leles!=ltms)
			return NULL;
	}
	if(ldsts!=ltms)
		return NULL;
	PyObject *iter = PyObject_GetIter(objtms);
	if (!iter) {
		// error not iterator
        return NULL;
	}
	int * tms = malloc(sizeof(int)*ltms);
	if(tms==NULL) {
		// out of memory
		return NULL;
	}
	float * dsts = malloc(sizeof(int)*ltms);
	if(dsts==NULL) {
		// out of memory
		return NULL;
	}
	int * eles = malloc(sizeof(int)*ltms);
	if(eles==NULL) {
		// out of memory
		return NULL;
	}
	int i=0;
	while (1) {
		PyObject *n = PyIter_Next(iter);
		if (!n) {
			// nothing left in the iterator
			break;
		}

		if (!PyInt_Check(n)) {
			// error, we were expecting an int
			free(tms);
			free(dsts);
			free(eles);
			return NULL;
		}

		int v = PyInt_AsLong(n); //int will be enough
		tms[i] = v;
		i++;
	}
	iter = PyObject_GetIter(objdsts);
	i = 0;
	while (1) {
		PyObject *n = PyIter_Next(iter);
		if (!n) {
			// nothing left in the iterator
			break;
		}

		if (!PyFloat_Check(n)) {
			// error, we were expecting a floating point value
			free(tms);
			free(dsts);
			free(eles);
			return NULL;
		}

		double v = PyFloat_AsDouble(n);
		dsts[i] = v;
		i++;
	}
	iter = PyObject_GetIter(objeles);
	i = 0;
	while (1) {
		PyObject *n = PyIter_Next(iter);
		if (!n) {
			// nothing left in the iterator
			break;
		}

		if (!PyInt_Check(n)) {
			// error, we were expecting an int
			free(tms);
			free(dsts);
			free(eles);
			return NULL;
		}

		int v = PyInt_AsLong(n); //int will be more than enough
		eles[i] = v;
		i++;
	}
	//TODO
	
	free(tms);
	free(dsts);
	free(eles);
    return Py_BuildValue("i", 42);
}


// Register module methods in __init__
static PyMethodDef module_methods[] = {
   { "compute", (PyCFunction)maxspd_compute, METH_VARARGS, NULL },
   { "tst", (PyCFunction)maxspd_tst, METH_VARARGS, NULL },
   { NULL, NULL, 0, NULL }
};

PyMODINIT_FUNC
initmaxspd(void)
{
	PyObject *m;

    m = Py_InitModule("maxspd", module_methods);
    if (m == NULL)
        return;

}

