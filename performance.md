# VFBquery Performance Test Results

**Test Date:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')
**Git Commit:** 8ff2eec7423afbdf1dc8773cf3e674b6bf9a98fe
**Branch:** dev
**Workflow Run:** 17589292536

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

- **FBbt_00003748 Query Time**: 155.0068 seconds
- **VFB_00101567 Query Time**: 0.2188 seconds
- **Total Query Time**: 155.2256 seconds

🎉 **Result**: All performance thresholds met!

---
*Last updated: 2025-09-09 16:35:11 UTC*
