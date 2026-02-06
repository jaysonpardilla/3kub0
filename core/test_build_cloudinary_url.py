#!/usr/bin/env python
"""
Standalone test script to verify build_cloudinary_url() handles duplicated URLs correctly.
This version doesn't require Django setup - it tests the regex logic directly.
"""

import re

def build_cloudinary_url(public_id_or_url, cloud_name=None):
    """
    Construct a proper Cloudinary URL from a public_id or URL.
    
    IMPORTANT: This function is for DISPLAY only. Never store full URLs in the database.
    Store only the public_id (relative path like 'product_images/bg_x.png').
    
    Handles the following cases:
    1. Already a clean full URL (returns as-is)
    2. Duplicated URL pattern: https://res.cloudinary.com/.../https:/res.cloudinary.com/... (extracts public_id)
    3. Malformed URL with res.cloudinary.com (extracts public_id)
    4. Normal relative path (constructs full URL)
    """
    # Default cloud name for testing
    if not cloud_name:
        cloud_name = 'deyrmzn1x'
    
    try:
        if not public_id_or_url:
            return ''

        s = str(public_id_or_url).strip()

        # Case 0: Check for DUPLICATED URL pattern first (most common bug)
        # Pattern 1: https://res.cloudinary.com/cloud_name/image/upload/v123/https:/res.cloudinary.com/cloud_name/image/upload/public_id
        # Pattern 2: https://res.cloudinary.com/cloud_name/image/upload/v123/https://res.cloudinary.com/cloud_name/image/upload/public_id
        duplicated_pattern_v1 = r'https://res\.cloudinary\.com/[^/]+/image/upload/v\d+/https:/res\.cloudinary\.com/[^/]+/image/upload/(.+)$'
        duplicated_pattern_v2 = r'https://res\.cloudinary\.com/[^/]+/image/upload/v\d+/https://res\.cloudinary\.com/[^/]+/image/upload/(.+)$'
        
        duplicated_match = re.search(duplicated_pattern_v1, s) or re.search(duplicated_pattern_v2, s)
        if duplicated_match:
            public_id = duplicated_match.group(1)
            public_id = re.sub(r'^v\d+/', '', public_id)
            public_id = public_id.lstrip('/')
            if public_id and '.' not in public_id:
                public_id = f"{public_id}.png"
            if public_id:
                return f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"

        # Case 1: Already a clean full URL
        if s.startswith('https://res.cloudinary.com/'):
            s = re.sub(r'https:/res\.cloudinary\.com', 'https://res.cloudinary.com', s)
            s = re.sub(r'(https://res\.cloudinary\.com/[^/]+/image/upload/)v\d+/https://', r'\1', s)
            return s
        
        # Case 2: Contains res.cloudinary.com but is malformed
        if 'res.cloudinary.com' in s:
            parts = s.split('/')
            public_part = None
            for i in range(len(parts) - 1, -1, -1):
                part = parts[i]
                if '.' in part and not part.startswith('http'):
                    candidate = '/'.join(parts[i:])
                    candidate = re.sub(r'^v\d+/', '', candidate)
                    candidate = re.sub(r'https:?/?/?res\.cloudinary\.com/?', '', candidate)
                    candidate = re.sub(r'^/?/?', '', candidate)
                    if candidate and not candidate.startswith('http'):
                        public_part = candidate
                        break
            
            if public_part:
                if '.' in public_part:
                    base, ext = public_part.rsplit('.', 1)
                    if len(ext) <= 4:
                        return f"https://res.cloudinary.com/{cloud_name}/image/upload/{base}.{ext}"
                return f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_part}.png"
            
            return ''
        
        # Case 3: Normal relative path
        s = s.lstrip('/')
        
        if '/image/upload/' in s:
            s = s.split('/image/upload/')[-1]
        
        s = re.sub(r'^v\d+/', '', s)
        
        if '.' in s:
            base, ext = s.rsplit('.', 1)
            if len(ext) <= 4:
                return f"https://res.cloudinary.com/{cloud_name}/image/upload/{base}.{ext}"
        
        return f"https://res.cloudinary.com/{cloud_name}/image/upload/{s}.png"
        
    except Exception:
        return ''


def test_build_cloudinary_url():
    """Test various URL patterns to ensure duplicated URLs are handled correctly."""
    
    test_cases = [
        # Case 1: Duplicated URL (the main issue)
        {
            'input': 'https://res.cloudinary.com/deyrmzn1x/image/upload/v1770309922/https:/res.cloudinary.com/deyrmzn1x/image/upload/product_images/bg_hinata_pjujcx.png',
            'expected': 'https://res.cloudinary.com/deyrmzn1x/image/upload/product_images/bg_hinata_pjujcx.png',
            'description': 'Duplicated URL with version number'
        },
        # Case 2: Clean full URL
        {
            'input': 'https://res.cloudinary.com/deyrmzn1x/image/upload/product_images/bg_test.png',
            'expected': 'https://res.cloudinary.com/deyrmzn1x/image/upload/product_images/bg_test.png',
            'description': 'Clean full URL'
        },
        # Case 3: Relative path
        {
            'input': 'product_images/bg_test.png',
            'expected': 'https://res.cloudinary.com/deyrmzn1x/image/upload/product_images/bg_test.png',
            'description': 'Relative path'
        },
        # Case 4: Empty string
        {
            'input': '',
            'expected': '',
            'description': 'Empty string'
        },
        # Case 5: User profile relative path
        {
            'input': 'user_profiles/FB_IMG_1729318205270_heblrn',
            'expected': 'https://res.cloudinary.com/deyrmzn1x/image/upload/user_profiles/FB_IMG_1729318205270_heblrn.png',
            'description': 'User profile relative path (no extension)'
        },
        # Case 6: Category relative path with extension (or treated as no extension since no .png/.jpg)
        {
            'input': 'product_category/488fa53fdc93c8ba22b0bf884f90ea39-removebg-preview_sj6uzk',
            'expected': 'https://res.cloudinary.com/deyrmzn1x/image/upload/product_category/488fa53fdc93c8ba22b0bf884f90ea39-removebg-preview_sj6uzk.png',
            'description': 'Category relative path (no standard extension, adding .png)'
        },
        # Case 7: Another duplicated URL pattern with https://
        {
            'input': 'https://res.cloudinary.com/deyrmzn1x/image/upload/v123/https://res.cloudinary.com/deyrmzn1x/image/upload/product_images/bg_lettuce.png',
            'expected': 'https://res.cloudinary.com/deyrmzn1x/image/upload/product_images/bg_lettuce.png',
            'description': 'Duplicated URL with https:// pattern'
        },
    ]
    
    print("=== Testing build_cloudinary_url() ===\n")
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        input_url = test_case['input']
        expected = test_case['expected']
        description = test_case['description']
        
        result = build_cloudinary_url(input_url)
        
        if result == expected:
            print(f"[PASS] Test {i}: {description}")
            print(f"  Input:    {input_url}")
            passed += 1
        else:
            print(f"[FAIL] Test {i}: {description}")
            print(f"  Input:    {input_url}")
            print(f"  Expected: {expected}")
            print(f"  Got:      {result}")
            failed += 1
        
        print()
    
    # Test with None
    print("Test with None:")
    result = build_cloudinary_url(None)
    if result == '':
        print(f"[PASS] None test passed: got empty string")
        passed += 1
    else:
        print(f"[FAIL] None test failed: got {result}")
        failed += 1
    
    print()
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n[SUCCESS] All tests passed! The build_cloudinary_url() function is working correctly.")
    else:
        print(f"\n[ERROR] {failed} test(s) failed. Please check the implementation.")
    
    return failed == 0

if __name__ == '__main__':
    success = test_build_cloudinary_url()
    exit(0 if success else 1)
