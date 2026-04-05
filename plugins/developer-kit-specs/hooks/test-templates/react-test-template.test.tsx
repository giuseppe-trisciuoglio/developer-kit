// Reference template for React test generation. Not loaded at runtime —
// the generator builds test content programmatically via render_typescript(react=True).
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('{{TEST_TITLE}}', () => {
  {{TEST_METHODS}}
});
