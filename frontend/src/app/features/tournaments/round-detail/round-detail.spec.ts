import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RoundDetail } from './round-detail';

describe('RoundDetail', () => {
  let component: RoundDetail;
  let fixture: ComponentFixture<RoundDetail>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RoundDetail],
    }).compileComponents();

    fixture = TestBed.createComponent(RoundDetail);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
