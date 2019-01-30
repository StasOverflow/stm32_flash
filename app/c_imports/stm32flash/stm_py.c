#include <Python.h>
#include "structmember.h"

#include <sys/types.h>
#include <sys/stat.h>
#include <stdint.h>
#include <stdbool.h>
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

static void close_with_argument( PyObject *self, int ret );

static PyObject* polled_method(PyObject * self, PyObject * args, PyObject * keywds);
static PyObject* pull_method(PyObject * self, PyObject * args, PyObject * keywds);


#define DEFAULT_GPIO_SEQ                "rts,dtr"

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

static const char *action2str(enum actions act);
//static void err_multi_action(enum actions new);
static int is_addr_in_ram(uint32_t addr);
static int is_addr_in_flash(uint32_t addr);
/* returns the page that contains address "addr" */
static int flash_addr_to_page_floor(uint32_t addr);
/* returns the first page whose start addr is >= "addr" */
int flash_addr_to_page_ceil(uint32_t addr);
/* returns the lower address of flash page "page" */
static uint32_t flash_page_to_addr(int page);

/***********************************************************************************************************************
 *
 *      Port-dependant structures and methods, settings structure is filled with values from start
 *
 **********************************************************************************************************************/
static struct port_options port_opts = {
	.device			    = "COM5",
	.baudRate		    = SERIAL_BAUD_57600,
	.serial_mode		= "8e1",
	.bus_addr		    = 0,
	.rx_frame_max		= STM32_MAX_RX_FRAME,
	.tx_frame_max		= STM32_MAX_TX_FRAME,
};
static struct port_interface   *port = NULL;
static PyObject* open_da_port(PyObject *self, PyObject *args, PyObject *keywds);
static PyObject* close_da_port(PyObject *self, PyObject *args);


static PyObject* open_da_port(PyObject *self, PyObject *args, PyObject *keywds)
{
    const char          *device         =   port_opts.device;
    long                baudrate        =   serial_get_baud_int(port_opts.baudRate);

    static char *kwlist[] = {"device", "baudrate", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "|sl", kwlist, &device, &baudrate))
    {
        return NULL;
    }

    PyObject *argsumentios =  Py_BuildValue("()");

    printf("dernem pythonom \n");

    PyObject *myobject_method = PyObject_GetAttrString(self, "port_close");

    PyObject *result = PyObject_Call(myobject_method, argsumentios, NULL);

    Py_XDECREF(argsumentios);
    Py_XDECREF(myobject_method);
    Py_XDECREF(result);

    port_opts.device = device;
    port_opts.baudRate = serial_get_baud(baudrate);


    printf("Portopts struct is now %s\n", port_opts.device);

    if (port_open(&port_opts, &port) != PORT_ERR_OK)
    {
		printf("Failed to open port: %s\n", port_opts.device);
		close_with_argument(self, 1);
		return Py_None;
	}
	else
	{
		printf("Successfully opened port %s\n", port_opts.device);
		printf("With baudrate %d\t\n", serial_get_baud_int(port_opts.baudRate));
		printf("With serial mode %s\t\n", port_opts.serial_mode);
		printf("With bus addres %d\t\n", port_opts.bus_addr);
		printf("with rx_max %d of %d\t\n", port_opts.rx_frame_max, STM32_MAX_RX_FRAME);
		printf("with tx_max %d of %d\t\n", port_opts.tx_frame_max, STM32_MAX_TX_FRAME);
	}

	if( port )
	{
	    printf("Interface %s: %s\n", port->name, port->get_cfg_str(port));
	}

    Py_XDECREF(kwlist);
    Py_XDECREF(args);
    Py_XDECREF(keywds);

	return Py_None;
}


static PyObject* close_da_port(PyObject *self, PyObject *args)
{
	if (port)
	{
        printf("there were an instance of a port opened before, so close it \n");
		port->close(port);
		port = NULL;
		printf("Port closed \n");
	}
	else
	{
	    printf("Error closing port \n");
	}

    Py_XDECREF(args);

	return Py_None;
}
/***********************************************************************************************************************
 *
 *      Parser-dependant structures and methods
 *
 **********************************************************************************************************************/
static void		    *p_st		        = NULL;
static parser_t	    *parser		        = NULL;

static PyObject* init_da_parser(PyObject * self, PyObject *args, PyObject *keywds)
{
    char            *file_path;
    int             action;
    bool            force_binary = 0;
	parser_err_t    perr;

    static char *kwlist[] = {"file_path", "action", "force_binary", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "si|p", kwlist, &file_path, &action, &force_binary))
    {
        return NULL;
    }

    printf("So the arguments are: \n");
    printf("path to file: %s \n", file_path);
    printf("action: %s\n", action2str(action));
    printf("binary_forcing %d\n", force_binary);

	if (action == ACT_WRITE)
	{
		// first try hex
		if (!force_binary)
		{
			parser = &PARSER_HEX;
			p_st = parser->init();
			if (!p_st)
			{
				printf("%s Parser failed to initialize\n", parser->name);
                close_with_argument(self, 1);
                return Py_None;
			}
		}

		if (force_binary || (perr = parser->open(p_st, file_path, 0)) != PARSER_ERR_OK)
		{
			if (force_binary || perr == PARSER_ERR_INVALID_FILE)
			{
				if (!force_binary)
				{
					parser->close(p_st);
					p_st = NULL;
				}

				// now try binary
				parser = &PARSER_BINARY;
				p_st = parser->init();
				if (!p_st)
				{
					printf("%s Parser failed to initialize\n", parser->name);
                    close_with_argument(self, 1);
                    return Py_None;
				}
				perr = parser->open(p_st, file_path, 0);
			}

			// if still have an error, fail
			if (perr != PARSER_ERR_OK)
			{
				printf("%s ERROR: %s\n", parser->name, parser_errstr(perr));
				if (perr == PARSER_ERR_SYSTEM)
				{
				    perror(file_path);
				}

                close_with_argument(self, 1);
                return Py_None;
			}
		}

		printf("Using Parser : %s\n", parser->name);
	} else {
		parser = &PARSER_BINARY;
		p_st = parser->init();
		if (!p_st)
		{
			printf("%s Parser failed to initialize\n", parser->name);

            close_with_argument(self, 1);
            return Py_None;
            // Insert Close goto close;
		}
	}

    Py_XDECREF(kwlist);
    Py_XDECREF(args);
    Py_XDECREF(keywds);

    return Py_None;
}

static PyObject* open_with_parser(PyObject * self, PyObject *args, PyObject *keywds)
{
    char *file_path;

    static char *kwlist[] = {"file_path", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "s|", kwlist, &file_path))
    {
        return NULL;
    }

    printf("file is %s \n", file_path);

    Py_XDECREF(kwlist);
    Py_XDECREF(args);
    Py_XDECREF(keywds);

    return Py_None;
}

static PyObject* close_da_parser(PyObject * self, PyObject * args)
{
	if (p_st)
	{
	    parser->close(p_st);
        p_st = NULL;
	}

    Py_XDECREF(args);

    return Py_None;
}
/***********************************************************************************************************************
 *
 *      STM-dependant structures and methods
 *
 **********************************************************************************************************************/
static stm32_t		    *stm        		    = NULL;

static PyObject* close_da_stm(PyObject * self, PyObject * args);
static PyObject* init_da_stm(PyObject * self, PyObject * args, PyObject * keywds);


static PyObject* init_da_stm(PyObject * self, PyObject * args, PyObject * keywds)
{
    bool init_flag = 1;
    char *gpio_seq = DEFAULT_GPIO_SEQ;

    static char *kwlist[] = {"init_flag", "gpio_seq", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "|ps", kwlist, &init_flag, &gpio_seq))
    {
        return NULL;
    }

//    close_da_stm(self, NULL);

    if( port )
    {
        if (init_flag && init_bl_entry(port, gpio_seq) == 0)
        {
            printf("Something went wrong with init bl stuff \n");
            close_with_argument(self, 1);
            return Py_None;
        }
        stm = stm32_init(port, init_flag);
        if (!stm)
        {
            printf("stm somehow didn't manage to launch \n");
            close_with_argument(self, 1);
            return Py_None;
        }
        else
        {
            printf("allrighty with stmio \n");
        }
    }
    else
    {
        // raise some ERROR: Unitialized based crap
        printf("INIT DA PORT AT THE FIRST PLACE, PLEASE \n");
		close_with_argument(self, 1);
		return Py_None;
    }

    Py_XDECREF(kwlist);
    Py_XDECREF(args);
    Py_XDECREF(keywds);

	return Py_None;
}


static PyObject* close_da_stm(PyObject * self, PyObject * args)
{
	if( stm )
	{
	    printf("There were an instance of stm, closing \n");
	    stm32_close(stm);
	}

    Py_XDECREF(args);

	return Py_None;
}

/***********************************************************************************************************************
 *
 *      Perform an action, based on the argument passed
 *
 **********************************************************************************************************************/

static PyObject *perform_da_action(PyObject *self, PyObject *args, PyObject * keywds)
{
    int             action;
    char            *file_path;
    unsigned long   start_addr      = 0;
    unsigned long   readwrite_len   = 0;
    int             no_erase        = 0;
    int				npages          = 0;
    int             spage           = 0;
    int             reset_flag      = 0;
    int             verify          = 0;
    int	            retry           = 10;
    int             exec_flag       = 0;
    unsigned long   execute_addr    = 0;

    static char     *kwlist[] = {
                        "action",
                        "file_path",
                        "start_addr",
                        "readwrite_len",
                        "no_erase",
                        "npages",
                        "spage",
                        "reset_flag",
                        "verify",
                        "retry",
                        "execute_flag",
                        "execute_addr"

                         NULL
                    };

    if( !PyArg_ParseTupleAndKeywords(
            args, keywds, "is|kkiiiiiiik", kwlist,
            &action, &file_path, &start_addr, &readwrite_len, &no_erase,
            &npages, &spage, &reset_flag, &verify, &retry, &exec_flag, &execute_addr
        ))
    {
        return NULL;
    }
    printf("action: %s \n", action2str(action));

    int ret = 1;

	uint8_t		            buffer[256];
	long unsigned int	    addr;
	long unsigned int       start;
	long unsigned int       end;
	unsigned int            len;
	int		                failed = 0;
	int		                first_page, num_pages;

    /*
     * Cleanup addresses:
     *
     * Starting from options
     *      start_addr, readwrite_len, spage, npages
     * and using device memory size, compute
     *      start, end, first_page, num_pages
     */

    if( !stm )
    {
        printf("im sorry, but you will have to initialize stm struct in the first place \n");
		close_with_argument(self, 1);
		return Py_None;
    }
    else
    {
        if( !p_st )
        {
            printf("Initiate the parser on the first place \n");
            close_with_argument(self, ret);
            return Py_None;
        }
        else
        {
            if (start_addr || readwrite_len)
            {
                start = start_addr;

                if (is_addr_in_flash(start))
                {
                    end = stm->dev->fl_end;
                }
                else
                {
                    no_erase = 1;
                    if (is_addr_in_ram(start))
                    {
                        end = stm->dev->ram_end;
                    }
                    else
                    {
                        end = start + sizeof(uint32_t);
                    }
                }

                if (readwrite_len && (end > start + readwrite_len))
                {
                    end = start + readwrite_len;
                }

                first_page = flash_addr_to_page_floor(start);
                if (!first_page && end == stm->dev->fl_end)
                {
                    num_pages = STM32_MASS_ERASE;
                }
                else
                {
                    num_pages = flash_addr_to_page_ceil(end) - first_page;
                }
            }
            else
            if (!spage && !npages)
            {
                start = stm->dev->fl_start;
                end = stm->dev->fl_end;
                first_page = 0;
                num_pages = STM32_MASS_ERASE;
            }
            else
            {
                first_page = spage;
                start = flash_page_to_addr(first_page);

                if (start > stm->dev->fl_end)
                {
                    printf("Address range exceeds flash size.\n");
                    close_with_argument(self, ret);
                    return Py_None;
                }

                if (npages)
                {
                    num_pages = npages;
                    end = flash_page_to_addr(first_page + num_pages);
                    if (end > stm->dev->fl_end)
                    {
                        end = stm->dev->fl_end;
                    }
                }
                else
                {
                    end = stm->dev->fl_end;
                    num_pages = flash_addr_to_page_ceil(end) - first_page;
                }

                if (!first_page && end == stm->dev->fl_end)
                {
                    num_pages = STM32_MASS_ERASE;
                }
            }


            parser_err_t            perr = 0;
            stm32_err_t             s_err;


            if (action == ACT_READ)
            {
                unsigned int max_len = port_opts.rx_frame_max;

                printf("Memory read\n");

                perr = parser->open(p_st, file_path, 1);
                if (perr != PARSER_ERR_OK)
                {
                    printf("%s ERROR: %s\n", parser->name, parser_errstr(perr));
                    if (perr == PARSER_ERR_SYSTEM)
                    {
                        perror(file_path);
                    }
                    close_with_argument(self, ret);
                    return Py_None;
                    // Insert Close goto close;
                }

                addr = start;
                while(addr < end)
                {
                    uint32_t left = end - addr;
                    len		= max_len > left ? left : max_len;
                    s_err = stm32_read_memory(stm, addr, buffer, len);
                    if (s_err != STM32_ERR_OK)
                    {
                        printf("Failed to read memory at address 0x%08lx, target write-protected?\n", addr);

                        close_with_argument(self, ret);
                        return Py_None;
                        // Insert Close goto close;
                    }
                    if (parser->write(p_st, buffer, len) != PARSER_ERR_OK)
                    {
                        printf("Failed to write data to file\n");

                        close_with_argument(self, ret);
                        return Py_None;
                        // Insert Close goto close;
                    }
                    addr += len;

                    // TODO: Replace this output with smth
        //            fprintf(diag,
        //                "\rRead address 0x%08x (%.2f%%) ",
        //                addr,
        //                (100.0f / (float)(end - start)) * (float)(addr - start)
        //            );
        //            fflush(diag);
                }

                printf("Done, now close all stuff\n");

                ret = 0;
                close_with_argument(self, ret);
                return Py_None;
                // Insert Close goto close;

                printf("Parser error: %s \n", parser_errstr(perr));
            }
            else
            if (action == ACT_READ_PROTECT)
            {
                printf("Read-Protecting flash\n");
                // the device automatically performs a reset after the sending the ACK
                reset_flag = 0;
                stm32_readprot_memory(stm);
                printf("Done.\n");
            }
            else
            if (action == ACT_READ_UNPROTECT)
            {
                printf("Read-UnProtecting flash\n");
                // the device automatically performs a reset after the sending the ACK
                reset_flag = 0;
                stm32_runprot_memory(stm);
                printf("Done.\n");
            }
            else
            if (action == ACT_ERASE_ONLY)
            {
                ret = 0;
                printf("Erasing flash\n");

                if (num_pages != STM32_MASS_ERASE &&
                    (start != flash_page_to_addr(first_page) || end != flash_page_to_addr(first_page + num_pages)))
                {
                    printf("Specified start & length are invalid (must be page aligned)\n");
                    ret = 1;
                    close_with_argument(self, ret);
                    return Py_None;
                }

                s_err = stm32_erase_memory(stm, first_page, num_pages);
                if (s_err != STM32_ERR_OK)
                {
                    printf("Failed to erase memory\n");
                    ret = 1;
                    close_with_argument(self, ret);
                    return Py_None;
                }
            }
            else
            if (action == ACT_WRITE_UNPROTECT)
            {
                printf("Write-unprotecting flash\n");
                // the device automatically performs a reset after the sending the ACK
                reset_flag = 0;
                stm32_wunprot_memory(stm);
                printf("Done.\n");

            }
            else
            if (action == ACT_WRITE)
            {
                printf("Write to memory\n");

                off_t 	offset = 0;
                ssize_t r;
                unsigned int size;
                unsigned int max_wlen, max_rlen;

                max_wlen = port_opts.tx_frame_max - 2;	// skip len and crc
                max_wlen &= ~3;	                        // 32 bit aligned

                max_rlen = port_opts.rx_frame_max;
                max_rlen = max_rlen < max_wlen ? max_rlen : max_wlen;

                ///Assume data from stdin is whole device
                if (file_path[0] == '-' && file_path[1] == '\0')
                {
                    size = end - start;
                }
                else
                {
                    size = parser->size(p_st);
                }

                // TODO: It is possible to write to non-page boundaries, by reading out flash
                //       from partial pages and combining with the input data
                // if ((start % stm->dev->fl_ps[i]) != 0 || (end % stm->dev->fl_ps[i]) != 0) {
                //	printf("Specified start & length are invalid (must be page aligned)\n");
                //	goto close;
                // }

                // TODO: If writes are not page aligned, we should probably read out existing flash
                //       contents first, so it can be preserved and combined with new data
                if (!no_erase && num_pages)
                {
                    printf("Erasing memory\n");
                    s_err = stm32_erase_memory(stm, first_page, num_pages);
                    if (s_err != STM32_ERR_OK)
                    {
                        printf("Failed to erase memory\n");
                        close_with_argument(self, ret);
                        return Py_None;
                    }
                }

//                fflush(diag);
                addr = start;
                while(addr < end && offset < size)
                {
                    uint32_t left	= end - addr;
                    len		= max_wlen > left ? left : max_wlen;
                    len		= len > size - offset ? size - offset : len;

                    if (parser->read(p_st, buffer, &len) != PARSER_ERR_OK)
                    {
                        close_with_argument(self, ret);
                        return Py_None;
                    }

                    if (len == 0)
                    {
                        if (file_path[0] == '-')
                        {
                            break;
                        }
                        else
                        {
                            close_with_argument(self, ret);
                            return Py_None;
                        }
                    }


                    while( failed < retry )
                    {
                        s_err = stm32_write_memory(stm, addr, buffer, len);
                        if (s_err != STM32_ERR_OK)
                        {
                            printf("Failed to write memory at address 0x%08lx\n", addr);
                            close_with_argument(self, ret);
                            return Py_None;
                        }
                        if (verify)
                        {
                            uint8_t compare[len];
                            unsigned int offset, rlen;

                            offset = 0;
                            while (offset < len)
                            {
                                rlen = len - offset;
                                rlen = rlen < max_rlen ? rlen : max_rlen;
                                s_err = stm32_read_memory(stm, addr + offset, compare + offset, rlen);
                                if (s_err != STM32_ERR_OK)
                                {
                                    printf("Failed to read memory at address 0x%08lx\n", addr + offset);
                                    close_with_argument(self, ret);
                                    return Py_None;
                                }
                                offset += rlen;
                            }

                            for(r = 0; r < len; ++r)
                            {
                                if (buffer[r] != compare[r])
                                {
                                    if (failed == retry)
                                    {
                                        printf("Failed to verify at address 0x%08x, expected 0x%02x and found 0x%02x\n",
                                            (uint32_t)(addr + r),
                                            buffer [r],
                                            compare[r]
                                        );
                                        close_with_argument(self, ret);
                                        return Py_None;
                                    }
                                    ++failed;
                                }
                            }
                        }
                    }
                    failed = 0;

                    addr	+= len;
                    offset	+= len;

//                    fprintf(diag,
//                        "\rWrote %saddress 0x%08x (%.2f%%) ",
//                        verify ? "and verified " : "",
//                        addr,
//                        (100.0f / size) * offset
//                    );
//                    fflush(diag);

                }

                printf("Done.\n");
                ret = 0;
                close_with_argument(self, ret);
                return Py_None;
            }
            else
            if (action == ACT_CRC)
            {
                unsigned long int crc_val = 0;

                printf("CRC computation\n");

                s_err = stm32_crc_wrapper(stm, start, end - start, (uint32_t *)&crc_val);
                if (s_err != STM32_ERR_OK)
                {
                    printf("Failed to read CRC\n");
                    close_with_argument(self, ret);
                    return Py_None;
                }
                printf("CRC(0x%08lx-0x%08lx) = 0x%08lx\n", start, end, crc_val);

                ret = 0;
                close_with_argument(self, ret);
                return Py_None;
            }
            else
            {
                printf("No concrette action specified \n");
                ret = 0;
                close_with_argument(self, ret);
                return Py_None;
            }
        }
    }

    return Py_None;
}


static PyObject* closing_sequence(PyObject * self, PyObject * args, PyObject * keywds)
{
    int                     reset_flag          = 0;
    int                     exec_flag		    = 0;
    unsigned long int		execute_addr        = 0;
    int		                ret                 = 1;
    char                    *gpio_seq           = DEFAULT_GPIO_SEQ;

    static char *kwlist[] = {"reset_flag", "exec_flag", "execute_addr", "ret", "gpio_seq", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "|iikis", kwlist,
                    &reset_flag, &exec_flag, &execute_addr, &ret, &gpio_seq)
       )
    {
        return NULL;
    }

    if( !stm )
    {
        printf("to close something, you need to open something at first \n");
    }
    else
    {
        if( !p_st )
        {
            if (stm && exec_flag && ret == 0)
            {
                if (execute_addr == 0)
                {
                    execute_addr = stm->dev->fl_start;
                }

                printf("\nStarting execution at address 0x%08lx... ", execute_addr);

    //            fflush(diag);
                if (stm32_go(stm, execute_addr) == STM32_ERR_OK)
                {
                    reset_flag = 0;
                    printf("done.\n");
                }
                else
                {
                    printf("failed.\n");
                }
            }

            if (stm && reset_flag)
            {
                printf("\nResetting device... ");

    //            fflush(diag);
                if (init_bl_exit(stm, port, gpio_seq))
                {
                    printf("done.\n");
                }
                else
                {
                    printf("failed.\n");
                }
            }
        }
    }

	if( p_st )
	{
	    printf("Closing parser \n");
	    parser->close(p_st);
	}

	if( stm )
	{
	    printf("Closing stm \n");
	    stm32_close  (stm);
	}

	if (port)
	{
	    printf("Closing port \n");
		port->close(port);
	}

    return Py_None;
//	fprintf(diag, "\n");
}
// Our Python binding to our C function
/* here we had some pyc function */

static PyMethodDef stm32_flash_methods[] = {
//    { "action", action, METH_VARARGS, "performs da main action" },
    { "port_open", (PyCFunction) open_da_port, METH_VARARGS | METH_KEYWORDS, "opens a port"},
    { "port_close", close_da_port, METH_NOARGS, "closes a port"},
    { "parser_init", (PyCFunction) init_da_parser, METH_VARARGS | METH_KEYWORDS, "inits either binary or hex parser"},
    { "parser_open", (PyCFunction) open_with_parser, METH_VARARGS | METH_KEYWORDS, "opens a file on a given path"},
    { "parser_close", (PyCFunction) close_da_parser, METH_NOARGS, "closes a parser"},
    { "stm_init",   (PyCFunction) init_da_stm,
                    METH_VARARGS | METH_KEYWORDS,
                    "inits stm with optional init flag and gpio seq"
    },
    { "stm_close",  (PyCFunction) close_da_stm, METH_NOARGS, "close stm struct or whatever" },
    { "action_perform", (PyCFunction) perform_da_action,
                    METH_VARARGS | METH_KEYWORDS,
                    "takes lots and lots of arguments which are going to and will be described a bit later"
    },
    { "close_all", (PyCFunction) closing_sequence,
                    METH_VARARGS | METH_KEYWORDS,
                    "performs finalizing actions, closes stuff all around"
    },
    { "polled_func", (PyCFunction) polled_method,
                    METH_VARARGS | METH_KEYWORDS,
                    "sample method"
    },
    { "pull", (PyCFunction) pull_method,
                    METH_VARARGS | METH_KEYWORDS,
                    "sample method namba 2"
    },
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


static PyObject* polled_method(PyObject * self, PyObject * args, PyObject * keywds)
{
    int arg1;
    char *arg2;
    unsigned long int arg3;

    static char *kwlist[] = {"arg1", "arg2", "arg3", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "isk|", kwlist, &arg1, &arg2, &arg3))
    {
        return NULL;
    }

    Py_XDECREF(kwlist);
    Py_XDECREF(args);
    Py_XDECREF(keywds);


    return Py_None;
}


static PyObject* pull_method(PyObject * self, PyObject * args, PyObject * keywds)
{
    int arg1 = 2;
    char *arg2 = "Sample Text";
    unsigned long arg3 = 8541116;

    static char *kwlist[] = {"arg1", "arg2", "arg3", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "|isk", kwlist, &arg1, &arg2, &arg3))
    {
        return NULL;
    }

    PyObject *argsumentios =  Py_BuildValue("()");;  // Py_BuildValue("(isk)", arg1, arg2, arg3);
    PyObject *keywords = PyDict_New();

    PyObject* argumentio1 = Py_BuildValue("i", arg1);
    PyObject* argumentio2 = Py_BuildValue("s", arg2);
    PyObject* argumentio3 = Py_BuildValue("k", arg3);

    PyDict_SetItem(keywords, PyUnicode_FromString("arg1"), argumentio1);
    PyDict_SetItemString(keywords, "arg2", argumentio2);
    PyDict_SetItem(keywords, PyUnicode_FromString("arg3"), argumentio3);

    PyObject *myobject_method = PyObject_GetAttrString(self, "polled_func");

    PyObject *result = PyObject_Call(myobject_method, argsumentios, keywords);

    Py_XDECREF(kwlist);
    Py_XDECREF(args);
    Py_XDECREF(keywds);

    Py_XDECREF(argumentio1);
    Py_XDECREF(argumentio2);
    Py_XDECREF(argumentio3);
    Py_XDECREF(argsumentios);
    Py_XDECREF(keywords);
    Py_XDECREF(myobject_method);
    Py_XDECREF(result);

    return Py_None;
}

static void close_with_argument( PyObject *self, int ret, int flag, unsigned long addr )
{
    PyObject *args = Py_BuildValue("()");
    PyObject *ret_val = Py_BuildValue("i", ret);
    PyObject *exec = Py_BuildValue("i", flag);
    PyObject *exec_addr = Py_BuildValue("k", addr);
    PyObject *keywords = PyDict_New();

    PyDict_SetItem(keywords, PyUnicode_FromString("ret"), ret_val);
    PyDict_SetItem(keywords, PyUnicode_FromString("exec_flag"), flag);
    PyDict_SetItem(keywords, PyUnicode_FromString("execute_addr"), addr);

    PyObject *myobject_method = PyObject_GetAttrString(self, "close_all");

    PyObject *result = PyObject_Call(myobject_method, args, keywords);

    Py_XDECREF(args);
    Py_XDECREF(ret_val);
    Py_XDECREF(exec);
    Py_XDECREF(exec_addr);
    Py_XDECREF(keywords);
    Py_XDECREF(exec_addr);
    Py_XDECREF(myobject_method);
    Py_XDECREF(result);
}

// Initializes our module using our above struct
PyMODINIT_FUNC PyInit_stm32_flash(void)
{
    PyObject* m;

    m = PyModule_Create(&stm32_flash_module);
    if (m == NULL)
    {
        printf("Module equals NULL \n");
        return NULL;
    }
    else
    {
        printf("Pymodule initialized \n");
    }

    return m;
}



/***********************************************************************************************************************
 *
 *  Some functions from a native version
 *
 **********************************************************************************************************************/
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

//static void err_multi_action(enum actions new)
//{
//	fprintf(stderr,
//		"ERROR: Invalid options !\n"
//		"\tCan't execute \"%s\" and \"%s\" at the same time.\n",
//		action2str(action), action2str(new));
//}

static int is_addr_in_ram(uint32_t addr)
{
	return addr >= stm->dev->ram_start && addr < stm->dev->ram_end;
}

static int is_addr_in_flash(uint32_t addr)
{
	return addr >= stm->dev->fl_start && addr < stm->dev->fl_end;
}

/* returns the page that contains address "addr" */
static int flash_addr_to_page_floor(uint32_t addr)
{
	int page;
	uint32_t *psize;

	if (!is_addr_in_flash(addr))
		return 0;

	page = 0;
	addr -= stm->dev->fl_start;
	psize = stm->dev->fl_ps;

	while (addr >= psize[0]) {
		addr -= psize[0];
		page++;
		if (psize[1])
			psize++;
	}

	return page;
}

/* returns the first page whose start addr is >= "addr" */
int flash_addr_to_page_ceil(uint32_t addr)
{
	int page;
	uint32_t *psize;

	if (!(addr >= stm->dev->fl_start && addr <= stm->dev->fl_end))
		return 0;

	page = 0;
	addr -= stm->dev->fl_start;
	psize = stm->dev->fl_ps;

	while (addr >= psize[0]) {
		addr -= psize[0];
		page++;
		if (psize[1])
			psize++;
	}

	return addr ? page + 1 : page;
}

/* returns the lower address of flash page "page" */
static uint32_t flash_page_to_addr(int page)
{
	int i;
	uint32_t addr, *psize;

	addr = stm->dev->fl_start;
	psize = stm->dev->fl_ps;

	for (i = 0; i < page; i++) {
		addr += psize[0];
		if (psize[1])
			psize++;
	}

	return addr;
}