#!/usr/bin/env python3
"""
Quick test to verify dynamic field support works
"""

from app.rule_engine.parser import parse_rules

def test_dynamic_fields():
    """Test that we can use any field name in WHERE and ASSIGN clauses"""
    
    # Test 1: Using type_id in WHERE clause (previously caused error)
    rules_dsl = '''
    rule "Type - Credit Fallback" where type:eq:"credit":i or type_id:eq:"1" assign type_id:1 category_id:16 priority 200;
    rule "Type - Debit Fallback" where type:eq:"debit":i assign type_id:2 category_id:15 priority 200;
    '''
    
    try:
        rules = parse_rules(rules_dsl)
        print("✓ Test 1 PASSED: type_id in WHERE clause works")
        print(f"  Parsed {len(rules)} rules successfully")
    except Exception as e:
        print(f"✗ Test 1 FAILED: {e}")
        return False
    
    # Test 2: Using custom dynamic fields
    custom_rules = '''
    rule "Custom Fields" where custom_field:eq:"test" assign custom_output:123 another_field:456 priority 100;
    '''
    
    try:
        rules = parse_rules(custom_rules)
        print("✓ Test 2 PASSED: Custom dynamic fields work")
        print(f"  Rule assignments: {rules[0].assignment.fields}")
    except Exception as e:
        print(f"✗ Test 2 FAILED: {e}")
        return False
    
    # Test 3: Mix of standard and custom fields
    mixed_rules = '''
    rule "Mixed Fields" where entity_name:c:"TEST" and type_id:eq:"1" assign category_id:5 custom_field:999 priority 50;
    '''
    
    try:
        rules = parse_rules(mixed_rules)
        print("✓ Test 3 PASSED: Mixed standard and custom fields work")
        print(f"  Rule assignments: {rules[0].assignment.fields}")
    except Exception as e:
        print(f"✗ Test 3 FAILED: {e}")
        return False
    
    print("\n✓ All tests PASSED! Dynamic fields are working correctly.")
    return True

if __name__ == "__main__":
    test_dynamic_fields()
