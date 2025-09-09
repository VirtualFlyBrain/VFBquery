# VFBquery Performance Test Results

**Test Date:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')
**Git Commit:** 0d7a24ca023f22a1ee6f2af49593b3d28e9f3a16
**Branch:** dev
**Workflow Run:** 17586236155

## Test Overview

This performance test measures the execution time of VFB term info queries for specific terms:

- **FBbt_00003748**: mushroom body (anatomical class)
- **VFB_00101567**: individual anatomy data

## Performance Thresholds

- Maximum single query time: 5 minutes (300 seconds)
- Maximum total time for both queries: 7.5 minutes (450 seconds)

### Performance Levels

- 🟢 **Excellent**: < 1 minute total
- 🟡 **Good**: 1-3 minutes total
- 🟠 **Acceptable**: 3-5 minutes total  
- 🔴 **Slow**: > 5 minutes total

*Note: Complex anatomical class queries can take 2-3 minutes due to extensive data processing, while individual anatomy queries are typically much faster.*

## Test Results

```
$(cat performance_test_output.log)
```

## Summary

✅ **Test Status**: Performance test completed

- **FBbt_00003748 Query Time**: 208.5962 seconds
- **VFB_00101567 Query Time**: 0.2191 seconds
- **Total Query Time**: 208.8153 seconds

⚠️ **Result**: Some performance thresholds exceeded or test failed

---
*Last updated: 2025-09-09 14:42:38 UTC*
