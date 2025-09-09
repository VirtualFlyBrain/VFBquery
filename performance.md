# VFBquery Performance Test Results

**Test Date:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')
**Git Commit:** 378e9f727b36873e40ab8fcf9a931a90e2fa09a3
**Branch:** dev
**Workflow Run:** 17594774704

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

- **FBbt_00003748 Query Time**: 1.1609 seconds
- **VFB_00101567 Query Time**: 0.7988 seconds
- **Total Query Time**: 1.9597 seconds

🎉 **Result**: All performance thresholds met!

---
*Last updated: 2025-09-09 20:27:06 UTC*
