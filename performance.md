# VFBquery Performance Test Results

**Test Date:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')
**Git Commit:** ae4061604ba14c11fb5ac6145c4604c34f365619
**Branch:** dev
**Workflow Run:** 17595864510

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

- **FBbt_00003748 Query Time**: 1.1024 seconds
- **VFB_00101567 Query Time**: 1.0704 seconds
- **Total Query Time**: 2.1728 seconds

🎉 **Result**: All performance thresholds met!

---
*Last updated: 2025-09-09 21:15:40 UTC*
