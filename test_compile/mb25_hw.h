/* mb25_hw.h - Hardware access functions for MBASIC compiler */
#ifndef MB25_HW_H
#define MB25_HW_H

/* I/O port access */
unsigned char mb25_inp(unsigned int port) __z88dk_fastcall;
void mb25_outp(unsigned int port, unsigned char value) __z88dk_callee;

/* Memory access */
unsigned char mb25_peek(unsigned int addr) __z88dk_fastcall;
void mb25_poke(unsigned int addr, unsigned char value) __z88dk_callee;

/* Convenience macros for direct use */
#define PEEK(addr) (*((unsigned char*)(addr)))
#define POKE(addr,val) (*((unsigned char*)(addr)) = (val))
#define INP(port) mb25_inp(port)
#define OUT(port,val) mb25_outp(port,val)

/* WAIT for port condition */
void mb25_wait(unsigned int port, unsigned char mask, unsigned char expected);

#endif /* MB25_HW_H */