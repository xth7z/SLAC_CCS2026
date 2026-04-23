/*
See LICENSE-original.txt for this sample’s licensing information.

Abstract:
A shader that adds two arrays of floats.
*/

#include <metal_stdlib>
#include <metal_atomic>
using namespace metal;

kernel void GPU_prime(device uint* inA,
                        device uint* inB,
                       device uint* result,
                       uint2 index [[thread_position_in_grid]])
{
    uint x=index.x;
    result[0]=inA[inB[x]];
    result[1]=inA[inB[x]+16];
}

kernel void GPU_write(device uint* inA,
                        device uint* inB,
                        device uint* result,
                       uint2 index [[thread_position_in_grid]])
{
    uint x=index.x;
    inA[inB[x]]=0;
}

kernel void read(device uint* inA,
                       device uint* result,
                       uint2 index [[thread_position_in_grid]])
{
    uint x=index.x;
    result[0]=inA[x*32];
}
