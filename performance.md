# VFBquery Performance Test Results

**Test Date:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')
**Git Commit:** 170e6e6dce2661e29b1595f7ac4d01831a105a7c
**Branch:** dev
**Workflow Run:** 17617786676

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

- **FBbt_00003748 Query Time**: 1.5989 seconds
- **VFB_00101567 Query Time**: 1.4164 seconds
- **Total Query Time**: 3.0153 seconds

🎉 **Result**: All performance thresholds met!

---
*Last updated: 2025-09-10 14:55:10 UTC*
