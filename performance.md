# VFBquery Performance Test Results

**Test Date:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')
**Git Commit:** c5477a8fa7c5ed6f0b2094eff54dd0d602c78acc
**Branch:** dev
**Workflow Run:** 17615683567

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

- **FBbt_00003748 Query Time**: 1.2194 seconds
- **VFB_00101567 Query Time**: 0.8992 seconds
- **Total Query Time**: 2.1186 seconds

🎉 **Result**: All performance thresholds met!

---
*Last updated: 2025-09-10 13:41:04 UTC*
