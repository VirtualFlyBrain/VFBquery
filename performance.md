# VFBquery Performance Test Results

**Test Date:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')
**Git Commit:** 4d7dac94b0933342d8ae9e28f4a0c690a5e277d2
**Branch:** dev
**Workflow Run:** 17619355295

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

- **FBbt_00003748 Query Time**: 1.5050 seconds
- **VFB_00101567 Query Time**: 0.9741 seconds
- **Total Query Time**: 2.4791 seconds

🎉 **Result**: All performance thresholds met!

---
*Last updated: 2025-09-10 15:51:38 UTC*
