#pragma once

#include <maya/MVector.h>
#include <maya/MMatrix.h>
#include <math.h>


inline MVector getPosition(const MMatrix & matrix) { return MVector(matrix[3][0], matrix[3][1], matrix[3][2]); }

inline double getDistance(const MVector &start, const MVector &end) { return (end - start).length(); }

inline MMatrix matrixFromVector(const MVector &translate)
{
    double matrix[4][4] = {{1, 0, 0, 0}, {0, 1, 0, 0}, {0, 0, 1, 0}, {translate.x, translate.y, translate.z, 1}};
    return MMatrix(matrix);
}

inline MVector getDirection(const MVector &start, const MVector &end)
{
    MVector direction = end - start;
    direction.normalize();
    return direction;
}

template <typename T>
inline T lerp(const T &a, const T &b, const T &f) { return (a * (1.0 - f)) + (b * f); }

template <typename T, typename C>
inline T lerp(const T &a, const T &b, const C &f) { return (a * (1.0 - f)) + (b * f); }