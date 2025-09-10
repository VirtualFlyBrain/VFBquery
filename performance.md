# VFBquery Performance Test Results

**Test Date:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')
**Git Commit:** ed1993e5fdc2ab082eaf718f9daee32c0f3c9c48
**Branch:** dev
**Workflow Run:** 17616658994

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

- **FBbt_00003748 Query Time**: 1.5013 seconds
- **VFB_00101567 Query Time**: 1.2714 seconds
- **Total Query Time**: 2.7727 seconds

🎉 **Result**: All performance thresholds met!

---
*Last updated: 2025-09-10 14:15:51 UTC*
