#include <Python.h>
#include "hellomodule.h"
#include "fibbonacious.h"

// Function 1: A simple 'hello world' function
static PyObject* helloworld(PyObject* self, PyObject* args) 
{   
    printf("Hello World, %s\n", DADA);
    return Py_None;
}


// Our Python binding to our C function
// This will take one and only one non-keyword argument
static PyObject* fib(PyObject* self, PyObject* args)
{
    // instantiate our `n` value
    int n;
    // if our `n` value 
    if(!PyArg_ParseTuple(args, "i", &n))
        return NULL;
    // return our computed fib number
    return Py_BuildValue("i", Cfib(n));
}

// Our Module's Function Definition struct
// We require this `NULL` to signal the end of our method
// definition 
static PyMethodDef myMethods[] = {
    { "helloworld", helloworld, METH_NOARGS, "Prints Hello World" },
    { "fibo", fib, METH_VARARGS, "Prints Hello World" },
    { NULL, NULL, 0, NULL }
};

// Our Module Definition struct
static struct PyModuleDef myModule = {
    PyModuleDef_HEAD_INIT,
    "myModule",
    "Test Module",
    -1,
    myMethods
};

// Initializes our module using our above struct
PyMODINIT_FUNC PyInit_stm32_flash(void)
{
    return PyModule_Create(&myModule);
}