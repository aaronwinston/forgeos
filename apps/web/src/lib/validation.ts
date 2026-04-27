import { z } from 'zod';

// Email validation schema
export const emailSchema = z.string().email('Invalid email address');

export function validateEmail(email: string): { valid: boolean; error?: string } {
  const result = emailSchema.safeParse(email);
  if (!result.success) {
    return { valid: false, error: result.error.errors[0]?.message };
  }
  return { valid: true };
}

// URL validation schema - ensures safe URLs with http/https protocols
export const urlSchema = z.string().url('Invalid URL').refine(
  (url) => {
    try {
      const parsed = new URL(url);
      return parsed.protocol === 'http:' || parsed.protocol === 'https:';
    } catch {
      return false;
    }
  },
  { message: 'Only http:// and https:// protocols are allowed' }
);

export function validateUrl(url: string): { valid: boolean; error?: string } {
  const result = urlSchema.safeParse(url);
  if (!result.success) {
    return { valid: false, error: result.error.errors[0]?.message };
  }
  return { valid: true };
}

// Text length validation - max 5000 chars
export const textSchema = z.string().max(5000, 'Text must be 5000 characters or less');

export function validateTextLength(text: string, maxLength = 5000): { valid: boolean; error?: string } {
  const result = textSchema.max(maxLength).safeParse(text);
  if (!result.success) {
    return { valid: false, error: result.error.errors[0]?.message };
  }
  return { valid: true };
}

// Phone number validation - optional international format support
export const phoneSchema = z.string().refine(
  (phone) => {
    // Simple regex that allows:
    // +1234567890, (123) 456-7890, 123-456-7890, 123.456.7890, 1234567890
    const phoneRegex = /^[\d+\-().\s]{10,}$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
  },
  { message: 'Invalid phone number' }
);

export function validatePhoneNumber(phone: string): { valid: boolean; error?: string } {
  const result = phoneSchema.safeParse(phone);
  if (!result.success) {
    return { valid: false, error: result.error.errors[0]?.message };
  }
  return { valid: true };
}

// Password validation - minimum 8 chars, at least one uppercase, one lowercase, one number
export const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .refine(
    (pwd) => /[A-Z]/.test(pwd),
    'Password must contain at least one uppercase letter'
  )
  .refine(
    (pwd) => /[a-z]/.test(pwd),
    'Password must contain at least one lowercase letter'
  )
  .refine(
    (pwd) => /\d/.test(pwd),
    'Password must contain at least one number'
  );

export function validatePassword(password: string): { valid: boolean; error?: string } {
  const result = passwordSchema.safeParse(password);
  if (!result.success) {
    return { valid: false, error: result.error.errors[0]?.message };
  }
  return { valid: true };
}

// Organization/company name validation
export const orgNameSchema = z.string().min(1, 'Organization name is required').max(255, 'Organization name must be 255 characters or less');

export function validateOrgName(name: string): { valid: boolean; error?: string } {
  const result = orgNameSchema.safeParse(name);
  if (!result.success) {
    return { valid: false, error: result.error.errors[0]?.message };
  }
  return { valid: true };
}

// Generic text field validator
export function validateRequired(text: string, fieldName = 'Field'): { valid: boolean; error?: string } {
  if (!text || text.trim() === '') {
    return { valid: false, error: `${fieldName} is required` };
  }
  return { valid: true };
}

// Composite signin form validation
export function validateSignInForm(email: string, password: string): {
  valid: boolean;
  errors: { email?: string; password?: string };
} {
  const emailValidation = validateEmail(email);
  const passwordValidation = validateRequired(password, 'Password');

  if (!emailValidation.valid || !passwordValidation.valid) {
    return {
      valid: false,
      errors: {
        email: emailValidation.error,
        password: passwordValidation.error,
      },
    };
  }

  return { valid: true, errors: {} };
}

// Composite signup form validation
export function validateSignUpForm(email: string, password: string, orgName: string): {
  valid: boolean;
  errors: { email?: string; password?: string; orgName?: string };
} {
  const emailValidation = validateEmail(email);
  const passwordValidation = validatePassword(password);
  const orgValidation = validateOrgName(orgName);

  if (!emailValidation.valid || !passwordValidation.valid || !orgValidation.valid) {
    return {
      valid: false,
      errors: {
        email: emailValidation.error,
        password: passwordValidation.error,
        orgName: orgValidation.error,
      },
    };
  }

  return { valid: true, errors: {} };
}
