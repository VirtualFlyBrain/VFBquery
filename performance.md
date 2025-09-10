# VFBquery Performance Test Results

**Test Date:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')
**Git Commit:** 474f17f6562a2f56f0517d10925847a5f57bf320
**Branch:** dev
**Workflow Run:** 17620303405

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

- **FBbt_00003748 Query Time**: 1.2439 seconds
- **VFB_00101567 Query Time**: 1.2292 seconds
- **Total Query Time**: 2.4731 seconds

🎉 **Result**: All performance thresholds met!

---
*Last updated: 2025-09-10 16:28:55 UTC*
