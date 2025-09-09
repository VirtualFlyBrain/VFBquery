# VFBquery Performance Test Results

**Test Date:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')
**Git Commit:** 9552df492bad1fc6bfe63601e6be6caa717d35bb
**Branch:** dev
**Workflow Run:** 17592308736

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

❌ **Test Status**: Performance test failed to run properly

---
*Last updated: 2025-09-09 18:36:42 UTC*
