# VFBquery Performance Test Results

**Test Date:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')
**Git Commit:** 72c602f15edbf366806cf74524ae1c931f15a1ed
**Branch:** dev
**Workflow Run:** 17586988232

## Test Overview

This performance test measures the execution time of VFB term info queries for specific terms:

- **FBbt_00003748**: mushroom body (anatomical class)
- **VFB_00101567**: individual anatomy data

## Performance Thresholds

- Maximum single query time: 5 minutes (300 seconds)
- Maximum total time for both queries: 7.5 minutes (450 seconds)

## Test Results

```
$(cat performance_test_output.log)
```

## Summary

✅ **Test Status**: Performance test completed

- **FBbt_00003748 Query Time**: 125.0663 seconds
- **VFB_00101567 Query Time**: 0.1561 seconds
- **Total Query Time**: 125.2224 seconds

🎉 **Result**: All performance thresholds met!

---
*Last updated: 2025-09-09 15:07:50 UTC*
