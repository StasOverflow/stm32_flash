#include <Python.h>
#include "structmember.h"
#include <sys/types.h>
#include <sys/stat.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#include "init.h"
#include "utils.h"
#include "serial.h"
#include "stm32.h"
#include "parsers/parser.h"
#include "port.h"

#include "parsers/binary.h"
#include "parsers/hex.h"


enum actions {
	ACT_NONE,
	ACT_READ,
	ACT_WRITE,
	ACT_WRITE_UNPROTECT,
	ACT_READ_PROTECT,
	ACT_READ_UNPROTECT,
	ACT_ERASE_ONLY,
	ACT_CRC
};


typedef struct {
    PyObject_HEAD
    PyObject *first;
    PyObject *last;
    long int baudrate;
} Port;

static int
Port_traverse(Port *self, visitproc visit, void *arg)
{
    Py_VISIT(self->first);
    Py_VISIT(self->last);
    return 0;
}

static int
Port_clear(Port *self)
{
    Py_CLEAR(self->first);
    Py_CLEAR(self->last);
    return 0;
}

static void
Port_dealloc(Port* self)
{
    Port_clear(self);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject *
Port_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Port *self;

    self = (Port *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->first = PyUnicode_FromString("");
        if (self->first == NULL) {
            Py_DECREF(self);
            return NULL;
        }

        self->last = PyUnicode_FromString("");
        if (self->last == NULL) {
            Py_DECREF(self);
            return NULL;
        }

        self->baudrate = 9600;
    }

    return (PyObject *)self;
}

static int
Port_init(Port *self, PyObject *args, PyObject *kwds)
{
    PyObject *first=NULL, *last=NULL, *tmp;

    static char *kwlist[] = {"first", "last", "baudrate", NULL};

    if (! PyArg_ParseTupleAndKeywords(args, kwds, "|OOi", kwlist,
                                      &first, &last,
                                      &self->baudrate))
        return -1;

    if (first) {
        tmp = self->first;
        Py_INCREF(first);
        self->first = first;
        Py_XDECREF(tmp);
    }

    if (last) {
        tmp = self->last;
        Py_INCREF(last);
        self->last = last;
        Py_XDECREF(tmp);
    }

    return 0;
}


static PyMemberDef Port_members[] = {
    {"first", T_OBJECT_EX, offsetof(Port, first), 0,
     "first name"},
    {"last", T_OBJECT_EX, offsetof(Port, last), 0,
     "last name"},
    {"baudrate", T_INT, offsetof(Port, baudrate), 0,
     "baudrate value number"},
    {NULL}  /* Sentinel */
};

static PyObject *
Port_name(Port* self)
{
    if (self->first == NULL) {
        PyErr_SetString(PyExc_AttributeError, "first");
        return NULL;
    }

    if (self->last == NULL) {
        PyErr_SetString(PyExc_AttributeError, "last");
        return NULL;
    }

    return PyUnicode_FromFormat("%S %S", self->first, self->last);
}

static PyMethodDef Port_methods[] = {
    {"name", (PyCFunction)Port_name, METH_NOARGS,
     "Return the name, combining the first and last name"
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject PortOptType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "stm32_flash.Port",             /* tp_name */
    sizeof(Port),                   /* tp_basicsize */
    0,                              /* tp_itemsize */
    (destructor)Port_dealloc,       /* tp_dealloc */
    0,                              /* tp_print */
    0,                              /* tp_getattr */
    0,                              /* tp_setattr */
    0,                              /* tp_reserved */
    0,                              /* tp_repr */
    0,                              /* tp_as_number */
    0,                              /* tp_as_sequence */
    0,                              /* tp_as_mapping */
    0,                              /* tp_hash  */
    0,                              /* tp_call */
    0,                              /* tp_str */
    0,                              /* tp_getattro */
    0,                              /* tp_setattro */
    0,                              /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT |
        Py_TPFLAGS_BASETYPE |
        Py_TPFLAGS_HAVE_GC,         /* tp_flags */
    "Some objects",                 /* tp_doc */
    (traverseproc)Port_traverse,    /* tp_traverse */
    (inquiry)Port_clear,            /* tp_clear */
    0,                              /* tp_richcompare */
    0,                              /* tp_weaklistoffset */
    0,                              /* tp_iter */
    0,                              /* tp_iternext */
    Port_methods,                   /* tp_methods */
    Port_members,                   /* tp_members */
    0,                              /* tp_getset */
    0,                              /* tp_base */
    0,                              /* tp_dict */
    0,                              /* tp_descr_get */
    0,                              /* tp_descr_set */
    0,                              /* tp_dictoffset */
    (initproc)Port_init,            /* tp_init */
    0,                              /* tp_alloc */
    Port_new,                       /* tp_new */
};

static const char *action2str(enum actions act)
{
	switch (act) {
		case ACT_READ:
			return "memory read";
		case ACT_WRITE:
			return "memory write";
		case ACT_WRITE_UNPROTECT:
			return "write unprotect";
		case ACT_READ_PROTECT:
			return "read protect";
		case ACT_READ_UNPROTECT:
			return "read unprotect";
		case ACT_ERASE_ONLY:
			return "flash erase";
		case ACT_CRC:
			return "memory crc";
		default:
			return "";
	};
}

enum actions	act			        = ACT_NONE;
int				i_npages			= 0;
int             i_spage             = 0;
int             i_no_erase          = 0;
char			c_verify			= 0;
int				i_retry			    = 10;
char			c_exec_flag		    = 0;
uint32_t		u_execute			= 0;
char			c_init_flag		    = 1;
char			c_force_binary	    = 0;
char			c_reset_flag		= 0;
char			*pc_filename;
char			*pc_gpio_seq		= "rts,dtr";
uint32_t		u_start_addr		= 0;
uint32_t		u_readwrite_len	    = 0;


/*
 *  Device kinda global
 */
stm32_t		    *stm_struct		    = NULL;

void		    *v_p_st		        = NULL;
parser_t	    *parser_struct		= NULL;


static void error_multi_action(enum actions new_act)
{
	printf(
		"ERROR: Invalid options !\n"
		"\tCan't execute \"%s\" and \"%s\" at the same time.\n",
		action2str(act), action2str(new_act));
}

static int is_address_in_ram(uint32_t addr)
{
	return addr >= stm_struct->dev->ram_start && addr < stm_struct->dev->ram_end;
}

static int is_address_in_flash(uint32_t addr)
{
	return addr >= stm_struct->dev->fl_start && addr < stm_struct->dev->fl_end;
}

/* returns the page that contains address "addr" */
static int flash_address_to_page_floor(uint32_t addr)
{
	int page;
	uint32_t *psize;

	if (!is_address_in_flash(addr))
		return 0;

	page = 0;
	addr -= stm_struct->dev->fl_start;
	psize = stm_struct->dev->fl_ps;

	while (addr >= psize[0]) {
		addr -= psize[0];
		page++;
		if (psize[1])
			psize++;
	}

	return page;
}

/* returns the first page whose start addr is >= "addr" */
int flash_address_to_page_ceil(uint32_t addr)
{
	int page;
	uint32_t *psize;

	if (!(addr >= stm_struct->dev->fl_start && addr <= stm_struct->dev->fl_end))
		return 0;

	page = 0;
	addr -= stm_struct->dev->fl_start;
	psize = stm_struct->dev->fl_ps;

	while (addr >= psize[0]) {
		addr -= psize[0];
		page++;
		if (psize[1])
			psize++;
	}

	return addr ? page + 1 : page;
}

/* returns the lower address of flash page "page" */
static uint32_t flash_page_to_address(int page)
{
	int i;
	uint32_t addr, *psize;

	addr = stm_struct->dev->fl_start;
	psize = stm_struct->dev->fl_ps;

	for (i = 0; i < page; i++) {
		addr += psize[0];
		if (psize[1])
			psize++;
	}

	return addr;
}


static PyObject* open_da_port(PyObject *self, PyObject *args)
{
	struct port_interface   *port = NULL;
	stm32_err_t             s_err;
	parser_err_t            perr;
	int                     ret = 1;

    parser_struct = &PARSER_BINARY;
    v_p_st = parser_struct->init();
    if (!v_p_st) {
        printf("%s Parser failed to initialize\n", parser_struct->name);
        return Py_None;
    }
    else
    {
        printf("Parser init successfully \n");
    }

    /* settings */
    struct port_options port_options_struct = {
        .device			    = "COM5",
        .baudRate		    = 10,
        .serial_mode		= "8e1",
        .bus_addr		    = 0,
        .rx_frame_max		= STM32_MAX_RX_FRAME,
        .tx_frame_max		= STM32_MAX_TX_FRAME,
    };

    if (port_open(&port_options_struct, &port) != PORT_ERR_OK)
    {
		printf("Failed to open port: %s\n", port_options_struct.device);
		return Py_None;
	}
	else
	{
		printf("Successfully opened port %s\n", port_options_struct.device);
		printf("With baudrate %d\t\n", port_options_struct.baudRate);
		printf("With serial mode %s\t\n", port_options_struct.serial_mode);
		printf("With bus addres %d\t\n", port_options_struct.bus_addr);
		printf("with rx_max %d of %d\t\n", port_options_struct.rx_frame_max, STM32_MAX_RX_FRAME);
		printf("with tx_max %d of %d\t\n", port_options_struct.tx_frame_max, STM32_MAX_TX_FRAME);
	}

	if (c_init_flag && init_bl_entry(port, pc_gpio_seq) == 0)
	{
	    printf("Beda happened \n");
	    return Py_None;
	}
	else
	{
	    printf("We've passed dangerous initflagblentry sequence \n");
	}

	stm_struct = stm32_init(port, c_init_flag);
	if (!stm_struct)
	{
	    printf("Laja with stm happened \n");
	    return Py_None;
	}
	else
	{
	    printf("allrighty with stmio \n");
	}

	printf("Version      : 0x%02x\n", stm_struct->bl_version);
	if (port->flags & PORT_GVR_ETX) {
		printf("Option 1     : 0x%02x\n", stm_struct->option1);
		printf("Option 2     : 0x%02x\n", stm_struct->option2);
	}
	printf("Device ID    : 0x%04x (%s)\n", stm_struct->pid, stm_struct->dev->name);
	printf("- RAM        : %dKiB  (%db reserved by bootloader)\n", (
	                                                                stm_struct->dev->ram_end - 0x20000000) / 1024,
	                                                                stm_struct->dev->ram_start - 0x20000000
	                                                             );
	printf("- Flash      : %dKiB (size first sector: %dx%d)\n",
	       (stm_struct->dev->fl_end - stm_struct->dev->fl_start ) / 1024,
	        stm_struct->dev->fl_pps, stm_struct->dev->fl_ps[0]
        );
	printf("- Option RAM : %db\n", stm_struct->dev->opt_end - stm_struct->dev->opt_start + 1);
	printf("- System RAM : %dKiB\n", (stm_struct->dev->mem_end - stm_struct->dev->mem_start) / 1024);

	uint8_t		buffer[1024];
	uint32_t	addr, start, end;
	unsigned int	len;
	int		failed = 0;
	int		first_page, num_pages;


    /*
     * Address cleanup
     */
    if (u_start_addr || u_readwrite_len)
    {
		start = u_start_addr;

		if (is_address_in_flash(start))
		{
			end = stm_struct->dev->fl_end;
		}
		else
		{
			i_no_erase = 1;
			if (is_address_in_ram(start))
			{
				end = stm_struct->dev->ram_end;
			}
			else
			{
                end = start + sizeof(uint32_t);
			}
		}

		if (u_readwrite_len && (end > start + u_readwrite_len))
        {
            end = start + u_readwrite_len;
        }

		first_page = flash_address_to_page_floor(start);
		if (!first_page && end == stm_struct->dev->fl_end)
		{
			num_pages = STM32_MASS_ERASE;
		}
		else
		{
			num_pages = flash_address_to_page_ceil(end) - first_page;
		}
	} else if (!i_spage && !i_npages)
	{
		start = stm_struct->dev->fl_start;
		end = stm_struct->dev->fl_end;
		first_page = 0;
		num_pages = STM32_MASS_ERASE;
	}
	else
	{
		first_page = i_spage;
		start = flash_page_to_address(first_page);
		if (start > stm_struct->dev->fl_end)
		{
			printf("Address range exceeds flash size.\n");

			return Py_None;
//			goto close;
	    }
	    else
	    {
            printf("Address in flash matches range. \n");
	    }

		if (i_npages)
		{
			num_pages = i_npages;
			end = flash_page_to_address(first_page + num_pages);
			if (end > stm_struct->dev->fl_end)
			{
				end = stm_struct->dev->fl_end;
			}
		}
		else
		{
			end = stm_struct->dev->fl_end;
			num_pages = flash_address_to_page_ceil(end) - first_page;
		}

		if (!first_page && end == stm_struct->dev->fl_end)
		{
		    printf("num pages = MASS ERASE\n");
			num_pages = STM32_MASS_ERASE;
		}
		else
		{
		    printf("num pages neq MASS ERASE\n");
		}


	}

    printf("Lets say the action is READ \n");
    act = ACT_READ;

    if (act == ACT_READ)
    {
		unsigned int max_len = port_options_struct.rx_frame_max;

		printf("Memory read\n");

        pc_filename = "./extremely_importante_filo.txt";

        printf("before file open \n");

		perr = parser_struct->open(v_p_st, pc_filename, 1);

		printf("after file open \n");
		if (perr != PARSER_ERR_OK) {
			printf("%s ERROR: %s\n", parser_struct->name, parser_errstr(perr));
			if (perr == PARSER_ERR_SYSTEM)
				perror(pc_filename);
			return Py_None;
		}

		addr = start;
		while(addr < end) {
			uint32_t left	= end - addr;
			len		= max_len > left ? left : max_len;
			s_err = stm32_read_memory(stm_struct, addr, buffer, len);
			if (s_err != STM32_ERR_OK) {
				printf("Failed to read memory at address 0x%08x, target write-protected?\n", addr);
				return Py_None;
			}

			if (parser_struct->write(v_p_st, buffer, len) != PARSER_ERR_OK)
			{
				printf("Failed to write data to file\n");
				return Py_None;
			}
			addr += len;

			printf("\rRead address 0x%08x (%.2f%%) ",
				    addr,
				    (100.0f / (float)(end - start)) * (float)(addr - start)
			);
		}
		printf("Done.\n");
		ret = 0;

//		goto close;
	}

    printf("Got here without returns and stuff \n");

	if( v_p_st )
	{
	    parser_struct->close(v_p_st);
	    printf("Parser closed \n");
	}
	else
	{
	    printf("Error closing v_p_st \n");
	}

	if( stm_struct )
	{
    	stm32_close(stm_struct);
    	printf("Stm32 closed \n");
	}
	else
	{
	    printf("Error closing stm_strukcha \n");
	}

	if (port)
	{
		port->close(port);
		printf("Port closed \n");
	}
	else
	{
	    printf("Error closing port \n");
	}

	Py_DECREF(args);
	return Py_None;
}

// Our Python binding to our C function
// This will take one and only one non-keyword argument
static PyObject* action(PyObject *self, PyObject *args)
{
	Py_ssize_t TupleSize = 0;
	
	TupleSize = PyTuple_Size(args);
	printf("typle size is %64Id \n", TupleSize);
	
	static char * array[20];
	PyObject *iterator = PyObject_GetIter(args);
	PyObject *item;
	int increment = 0;
	
	
	while ((item = PyIter_Next(iterator)))
	{
		PyObject * ascii_mystring=PyUnicode_AsASCIIString(PyUnicode_FromObject(item));
		array[increment++] = PyBytes_AsString(ascii_mystring);
		/* do something with item */
		
		printf("%s \n", array[increment-1]);
		
		/* release reference when done */
		Py_DECREF(item);
	}

//	main(TupleSize, array);
	
	Py_DECREF(args);
	printf("stuff decrefd\n");
	
    return Py_None;
}


static PyMethodDef stm32_flash_methods[] = {
    { "action", action, METH_VARARGS, "performs da main action" },
    { "port_open", open_da_port, METH_VARARGS, "opens a port with given cfg"},
    { NULL, NULL, 0, NULL }
};


// Our Module Definition struct
static struct PyModuleDef stm32_flash_module = {
    PyModuleDef_HEAD_INIT,
    "Stm32FlashModule",
    "STM32 FLASH Module",
    -1,
    stm32_flash_methods
};


// Initializes our module using our above struct
PyMODINIT_FUNC PyInit_stm32_flash(void)
{
    PyObject* m;

    if (PyType_Ready(&PortOptType) < 0)
    {
        printf("We are not ready yetto \n");
        return NULL;
    }

    m = PyModule_Create(&stm32_flash_module);
    if (m == NULL)
    {
        printf("Module equals ZERO \n");
        return NULL;
    }

    Py_INCREF(&PortOptType);
    PyModule_AddObject(m, "Port", (PyObject *)&PortOptType);
    return m;
}