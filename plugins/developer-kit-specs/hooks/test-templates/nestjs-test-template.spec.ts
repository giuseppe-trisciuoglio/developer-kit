// Reference template for NestJS test generation. Not loaded at runtime —
// the generator builds test content programmatically via render_typescript(nestjs=True).
import { Test, TestingModule } from '@nestjs/testing';

describe('{{TEST_TITLE}}', () => {
  let moduleRef: TestingModule;

  beforeEach(async () => {
    moduleRef = await Test.createTestingModule({
      providers: [],
      controllers: [],
    }).compile();
  });

  {{TEST_METHODS}}
});
