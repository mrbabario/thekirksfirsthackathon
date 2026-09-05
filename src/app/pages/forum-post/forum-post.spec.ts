import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ForumPost } from './forum-post';

describe('ForumPost', () => {
  let component: ForumPost;
  let fixture: ComponentFixture<ForumPost>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ForumPost],
    }).compileComponents();

    fixture = TestBed.createComponent(ForumPost);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
