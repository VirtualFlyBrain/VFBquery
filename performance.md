# VFBquery Performance Test Results

**Test Date:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')
**Git Commit:** 2cae5805d1fcc42562714cafea9f255b4e95c9b9
**Branch:** dev
**Workflow Run:** 17595192267

## Test Overview

This performance test measures the execution time of VFB term info queries for specific terms:

- **FBbt_00003748**: mushroom body (anatomical class)
- **VFB_00101567**: individual anatomy data

## Performance Thresholds

- Maximum single query time: 2 seconds
- Maximum total time for both queries: 4 seconds

## Test Results

```
$(cat performance_test_output.log)
```

## Summary

✅ **Test Status**: Performance test completed

- **FBbt_00003748 Query Time**: 1.0960 seconds
- **VFB_00101567 Query Time**: 0.8968 seconds
- **Total Query Time**: 1.9928 seconds

🎉 **Result**: All performance thresholds met!

---
*Last updated: 2025-09-09 20:46:12 UTC*
