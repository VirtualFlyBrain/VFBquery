# VFBquery Performance Test Results

**Test Date:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')
**Git Commit:** 2bbc9087a75ced7e9a2fbe5d51d2bb30929963d5
**Branch:** dev
**Workflow Run:** 17595352611

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

- **FBbt_00003748 Query Time**: 1.0536 seconds
- **VFB_00101567 Query Time**: 1.0304 seconds
- **Total Query Time**: 2.0839 seconds

🎉 **Result**: All performance thresholds met!

---
*Last updated: 2025-09-09 20:54:03 UTC*
