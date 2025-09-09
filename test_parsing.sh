#!/bin/bash

# Test script to simulate the GitHub Actions workflow parsing
# This helps verify our parsing logic works correctly

echo "Testing performance report generation..."

# Create mock test output
cat > test_output.log << 'EOF'
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... 
==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 1.3683 seconds
VFB_00101567 query took: 0.0500 seconds
Total time for both queries: 1.4183 seconds
==================================================
Performance test completed successfully!
ok

----------------------------------------------------------------------
Ran 1 test in 1.418s

OK
EOF

# Extract timing information (same logic as in the workflow)
if grep -q "Performance Test Results:" test_output.log; then
    echo "✅ Found performance results"
    
    if grep -q "FBbt_00003748 query took:" test_output.log; then
        TIMING1=$(grep "FBbt_00003748 query took:" test_output.log | sed 's/.*took: \([0-9.]*\) seconds.*/\1/')
        echo "- FBbt_00003748 Query Time: ${TIMING1} seconds"
    fi
    
    if grep -q "VFB_00101567 query took:" test_output.log; then
        TIMING2=$(grep "VFB_00101567 query took:" test_output.log | sed 's/.*took: \([0-9.]*\) seconds.*/\1/')
        echo "- VFB_00101567 Query Time: ${TIMING2} seconds"
    fi
    
    if grep -q "Total time for both queries:" test_output.log; then
        TOTAL_TIME=$(grep "Total time for both queries:" test_output.log | sed 's/.*queries: \([0-9.]*\) seconds.*/\1/')
        echo "- Total Query Time: ${TOTAL_TIME} seconds"
    fi
    
    if grep -q "OK" test_output.log; then
        echo "🎉 Result: All performance thresholds met!"
    elif grep -q "FAILED" test_output.log; then
        echo "⚠️ Result: Some performance thresholds exceeded or test failed"
    fi
else
    echo "❌ No performance results found"
fi

# Clean up
rm test_output.log

echo "Parsing test completed!"
