/* compile like 
 * gcc -g -O3 -march=native -mtune=native -ffast-math -fopenmp --std=gnu11 -lpython3.5m -I/usr/include/python3.5m/ -I/usr/lib/python3.5/site-packages/numpy/core/include/ -fPIC --shared -o life.so life.c
 */

#include <Python.h>
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/noprefix.h>
#include <assert.h>

#define NPY_TYPE NPY_UINT8
#define CTYPE uint8_t
static PyObject *
life(PyObject *dummy, PyObject *args)
{
    PyObject *arg1=NULL, *aout=NULL;
    PyArrayObject *arr1=NULL, *oarr=NULL;

    if (!PyArg_ParseTuple(args, "OO!", &arg1, 
        &PyArray_Type, &aout)) return NULL;

    arr1 = (PyArrayObject*) PyArray_FROM_OTF(arg1, NPY_TYPE, NPY_ARRAY_IN_ARRAY);
    if (arr1 == NULL) return NULL;
    oarr = (PyArrayObject*) PyArray_FROM_OTF(aout, NPY_TYPE, NPY_ARRAY_INOUT_ARRAY);
    if (oarr == NULL) goto fail;
    
    if (PyArray_NDIM(arr1) != 2 || PyArray_NDIM(oarr) != 2)
        goto fail;
    
    int n = PyArray_DIM(oarr, 0);
    assert(1234567 % n == (1234567 & (n-1)));
    if (PyArray_DIM(oarr, 0) != n || PyArray_DIM(oarr, 1) != n
     || PyArray_DIM(arr1, 0) != n || PyArray_DIM(arr1, 1) != n)
        goto fail;
        
    CTYPE* a = (CTYPE*) PyArray_DATA(arr1);
    CTYPE* out = (CTYPE*) PyArray_DATA(oarr);
    
    for (int i = 0; i < n*n; i++) {
        out[i] = 0;
    }

    int mask = n-1;
    for (int y = 0; y < n; y++) {
        for (int x = 0; x < n; x++) {
            int sum =
		    a[((x+1)&mask) + n*((y  )&mask)]	    
		  + a[((x+1)&mask) + n*((y+1)&mask)]	    
		  + a[((x+1)&mask) + n*((y-1)&mask)]	    
		  + a[((x  )&mask) + n*((y+1)&mask)]	    
		  + a[((x  )&mask) + n*((y-1)&mask)]	    
		  + a[((x-1)&mask) + n*((y+1)&mask)]	    
		  + a[((x-1)&mask) + n*((y  )&mask)]	    
		  + a[((x-1)&mask) + n*((y-1)&mask)]	    
		  ;
	    int old = a[x + n*y];
	    int res = 0;
	    switch(sum) {
	        case 0:
	        case 1:   res = 0;   break;
	        case 2:   res = old; break;
	        case 3:   res = 1;   break;
	        default:  res = 0;   break;
	    }

	    out[x + n*y] = res;
	}
    }

            
    Py_DECREF(arr1);
    Py_DECREF(oarr);
    Py_INCREF(aout);
    return aout;

 fail:
    Py_XDECREF(arr1);
    PyArray_XDECREF_ERR(oarr);
    return NULL;
}


static PyMethodDef life_Methods[] = {
    {"life",  life, METH_VARARGS,
     "Do one life iteration"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};


PyMODINIT_FUNC
initlife(void)
{
    
    import_array();

    (void) Py_InitModule("life", life_Methods);

}

